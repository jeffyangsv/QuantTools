import os
import sys
import time
import pandas as pd
from multiprocessing import Pool, RLock, freeze_support
from rich import print
from tqdm import tqdm
import CeLue
import func
import user_config as ucfg
from QUANTTOOLS.QAStockETL.QAFetch import QA_fetch_stock_all,QA_fetch_stock_om_all,QA_fetch_code_new
from QUANTAXIS.QAFetch.QAQuery_Advance import (QA_fetch_stock_day_adv,QA_fetch_index_day_adv)
from QUANTAXIS.QAFetch.QAQuery import (QA_fetch_stock_xdxr)
from QUANTAXIS import QA_fetch_stock_block,QA_fetch_index_list_adv
from QUANTTOOLS.QAStockETL.QAFetch import QA_fetch_stock_industryinfo_bytdxhy
import pytdx.reader.gbbq_reader
from  QUANTAXIS.QAUtil import (QA_util_today_str,QA_util_if_trade,QA_util_add_months,QA_util_date_int2str,DATABASE,
                               QA_util_get_real_date,
                               QA_util_get_next_day,
                               QA_util_today_str,
                               QA_util_get_last_day,
                               QA_util_get_trade_range
                               )




pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 300)

# 配置部分
start_date = ''
end_date = ''

# 变量定义
tdxpath = ucfg.tdx['tdx_path']
csvdaypath = ucfg.tdx['pickle']
已选出股票列表 = []
tdxgn_drop = ["ST板块",]   #要剔除的通达信概念 list类型。通达信软件中查看“概念板块”
tdxhy_drop = ["T110201","T110202","T110204"]    #要剔除的通达信行业 list类型。记事本打开 通达信目录\incon.dat，查看#TDXNHY标签的行业代码 全国地产：T110201，区域地产：T110202，房产服务：T110204

def make_stocklist_qa():
    #获取全部上市交易股票
    codes = QA_fetch_stock_om_all()
    blockdata = QA_fetch_stock_block()
    #获取要剔除的板块（概念）股票ID（ST板块）
    dropblockcode = list(blockdata[blockdata.blockname.isin(tdxgn_drop)]['code'].drop_duplicates())
    #通过行业分类查询股票（如地产相关）
    tdxhy_drop_info = QA_fetch_stock_industryinfo_bytdxhy(tdxhy_drop)
    #获取要剔除的行业股票信息
    drophycode = list(tdxhy_drop_info['code'].drop_duplicates())

    #codes = list(codes['code'])
    codes = codes.code.unique().tolist()
    #科创板，北交所股票
    code_688 = [i for i in codes if i.startswith('68') == True] + [i for i in codes if i.startswith('78') == True] + [i for i in codes if i.startswith('430') == True] + [i for i in codes if i.startswith('8') == True]
    #code_688 = [i for i in codes if i.startswith('688') == True] + [i for i in codes if i.startswith('787') == True] + [i for i in codes if i.startswith('789') == True] + [i for i in codes if i.startswith('8') == True]

    #新股，上市不超过60天
    code_new = QA_fetch_code_new(ndays=60)['code'].unique().tolist()
    #剔除板块、行业、科创、北交所、新股后的股票ID
    target_code = [i for i in codes if i not in dropblockcode + drophycode + code_688 + code_new]

    return target_code

def make_stocklist():
    # 要进行策略的股票列表筛选
    stocklist = [i[:-4] for i in os.listdir(ucfg.tdx['csv_lday'])]  # 去文件名里的.csv，生成纯股票代码list
    print(f'生成股票列表, 共 {len(stocklist)} 只股票')
    print(f'剔除通达信概念股票: {tdxgn_drop}')
    tmplist = []
    df = func.get_TDX_blockfilecontent("block_gn.dat")
    # 获取df中blockname列的值是ST板块的行，对应code列的值，转换为list。用filter函数与stocklist过滤，得出不包括ST股票的对象，最后转为list
    for i in tdxgn_drop:
        tmplist = tmplist + df.loc[df['blockname'] == i]['code'].tolist()
    stocklist = list(filter(lambda i: i not in tmplist, stocklist))
    print(f'剔除通达信行业股票: {tdxhy_drop}')
    tmplist = []
    df = pd.read_csv(ucfg.tdx['tdx_path'] + os.sep + 'T0002' + os.sep + 'hq_cache' + os.sep + "tdxhy.cfg",
                     sep='|', header=None, dtype='object')
    for i in tdxhy_drop:
        tmplist = tmplist + df.loc[df[2] == i][1].tolist()
    stocklist = list(filter(lambda i: i not in tmplist, stocklist))
    print("剔除科创板股票")
    code_688 = [i for i in stocklist if i.startswith('68') == True] + [i for i in stocklist if i.startswith('78') == True] + [i for i in stocklist if i.startswith('430') == True] + [i for i in stocklist if i.startswith('8') == True]

    # tmplist = []
    # for stockcode in stocklist:
    #     if stockcode[:2] != '68':
    #         tmplist.append(stockcode)
    stocklist = [i for i in stocklist if i not in code_688]
    return stocklist

def load_dict_stock(stocklist,start_date = '2021-01-01', end_date = QA_util_today_str()):
    starttime_tick = time.time()
    data = QA_fetch_stock_day_adv(stocklist, start_date, end_date).to_qfq().data.reset_index()
    # tq = tqdm(stocklist)
    # for stockcode in tq:
    #     tq.set_description(stockcode)
    #     pklfile = csvdaypath + os.sep + stockcode + '.pkl'
    #     # dict[stockcode] = pd.read_csv(csvfile, encoding='gbk', index_col=None, dtype={'code': str})
    #     dicttemp[stockcode] = pd.read_pickle(pklfile)
    print(f'载入完成 用时 {(time.time() - starttime_tick):.2f} 秒')
    return data

def run_celue1(stocklist, df_today, tqdm_position=None,runtype=None):
    if runtype == 'single':
        tq = tqdm(stocklist[:])
    else:
        tq = tqdm(stocklist[:], leave=False, position=tqdm_position)
    for stockcode in tq:
        tq.set_description(stockcode)
        pklfile = csvdaypath + os.sep + stockcode + '.pkl'
        df_stock = pd.read_pickle(pklfile)
        if df_today is not None:  # 更新当前最新行情，否则用昨天的数据
            df_stock = func.update_stockquote(stockcode, df_stock, df_today)
        df_stock['date'] = pd.to_datetime(df_stock['date'], format='%Y-%m-%d')  # 转为时间格式
        df_stock.set_index('date', drop=False, inplace=True)  # 时间为索引。方便与另外复权的DF表对齐合并
        celue1 = CeLue.Strategy1(df_stock, start_date=start_date, end_date=end_date, mode='fast')
        if not celue1:
            stocklist.remove(stockcode)
    return stocklist


def run_celue2(stocklist, HS300_signal, df_gbbq, df_today, tqdm_position=None,runtype=None):
    # if 'single' in sys.argv[1:]:
    if runtype == 'single':
        tq = tqdm(stocklist[:])
    else:
        tq = tqdm(stocklist[:], leave=False, position=tqdm_position)
    for stockcode in tq:
        tq.set_description(stockcode)
        pklfile = csvdaypath + os.sep + stockcode + '.pkl'
        df_stock = pd.read_pickle(pklfile)
        df_stock['date'] = pd.to_datetime(df_stock['date'], format='%Y-%m-%d')  # 转为时间格式
        df_stock.set_index('date', drop=False, inplace=True)  # 时间为索引。方便与另外复权的DF表对齐合并
        if '09:00:00' < time.strftime("%H:%M:%S", time.localtime()) < '16:00:00' \
                and 0 <= time.localtime(time.time()).tm_wday <= 4:
            df_today_code = df_today.loc[df_today['code'] == stockcode]
            df_stock = func.update_stockquote(stockcode, df_stock, df_today_code)
            # 判断今天是否在该股的权息日内。如果是，需要重新前复权
            now_date = pd.to_datetime(time.strftime("%Y-%m-%d", time.localtime()))
            if now_date in df_gbbq.loc[df_gbbq['code'] == stockcode]['权息日'].to_list():
                cw_dict = func.readall_local_cwfile()
                df_stock = func.make_fq(stockcode, df_stock, df_gbbq, cw_dict)
        celue2 = CeLue.Strategy2(df_stock, HS300_signal, start_date=start_date, end_date=end_date).iat[-1]
        if not celue2:
            stocklist.remove(stockcode)
    return stocklist

def gbbqload():
    # 解密通达信股本变迁文件
    starttime_tick = time.time()
    category = {
        '1': '除权除息', '2': '送配股上市', '3': '非流通股上市', '4': '未知股本变动', '5': '股本变化',
        '6': '增发新股', '7': '股份回购', '8': '增发新股上市', '9': '转配股上市', '10': '可转债上市',
        '11': '扩缩股', '12': '非流通股缩股', '13': '送认购权证', '14': '送认沽权证'}
    print(f'解密通达信gbbq股本变迁文件')
    filepath = 'E:/ghzq/T0002/hq_cache/gbbq'
    df_gbbq = pytdx.reader.gbbq_reader.GbbqReader().get_df(filepath)
    df_gbbq.drop(columns=['market'], inplace=True)
    df_gbbq.columns = ['code', '权息日', '类别',
                       '分红-前流通盘', '配股价-前总股本', '送转股-后流通盘', '配股-后总股本']
    df_gbbq['类别'] = df_gbbq['类别'].astype('object')
    df_gbbq['code'] = df_gbbq['code'].astype('object')
    for i in range(df_gbbq.shape[0]):
        df_gbbq.iat[i, df_gbbq.columns.get_loc("类别")] = category[str(df_gbbq.iat[i, df_gbbq.columns.get_loc("类别")])]
    df_gbbq.to_csv('E:/TDXdata' + os.sep + 'gbbq.csv', encoding='gbk', index=False)
    # 如果读取，使用下行命令
    # df_gbbq = pd.read_csv(ucfg.tdx['csv_cw'] + '/gbbq.csv', encoding='gbk', dtype={'code': 'object'})
    print(f'股本变迁解密完成 用时 {(time.time() - starttime_tick):>5.2f} 秒')
    # print(f'全部完成 用时 {(time.time() - starttime):>5.2f} 秒 程序结束')

def HS300_SIGNAL(index='000300',trading_date=QA_util_today_str()):
    # 策略部分
    # 先判断今天是否买入
    # print('今日HS300行情判断')
    #保存hs300行情到csv
    # func.day2csv(ucfg.tdx['tdx_path'] + '/vipdoc/sh/lday', 'sh000300.day', ucfg.tdx['csv_index'])
    # df_hs300 = pd.read_csv(ucfg.tdx['csv_index'] + '/000300.csv', index_col=None, encoding='gbk', dtype={'code': str})
    df_hs300_qa = QA_fetch_index_day_adv(index,'2020-01-01',trading_date).data[['open','high','low','close','vol','amount']]
    df_hs300_qa['vol'] = df_hs300_qa['vol'] * 100.0
    df_hs300_qa.reset_index(inplace=True)

    df_hs300_qa['date'] = pd.to_datetime(df_hs300_qa['date'], format='%Y-%m-%d')  # 转为时间格式
    df_hs300_qa.set_index('date', drop=False, inplace=True)  # 时间为索引。方便与另外复权的DF表对齐合并
    if '09:00:00' < time.strftime("%H:%M:%S", time.localtime()) < '15:30:00':
        df_today = func.get_tdx_lastestquote((1, index))
        df_hs300_qa = func.update_stockquote(index, df_hs300_qa, df_today)
        del df_today

    HS300_signal = CeLue.signalHS300(df_hs300_qa)
    # print(HS300_signal.iat[-1])
    if HS300_signal.iat[-1]:
        print('[red]今日HS300满足买入条件，执行买入操作[/red]')
    else:
        print('[green]今日HS300不满足买入条件，仍然选股，但不执行买入操作[/green]')
        HS300_signal.loc[:] = True  # 强制全部设置为True出选股结果
    return HS300_signal

def get_df_today(stocklist):
    # 周一到周五，9点到16点之间，获取在线行情。其他时间不是交易日，默认为离线数据已更新到最新
    df_today_tmppath = ucfg.tdx['csv_gbbq'] + '/df_today.pkl'
    if '09:00:00' < time.strftime("%H:%M:%S", time.localtime()) < '15:30:00' \
            and 0 <= time.localtime(time.time()).tm_wday <= 4:
        # 获取当前最新行情，临时保存到本地，防止多次调用被服务器封IP。
        print(f'现在是交易时段，需要获取股票实时行情')
        if os.path.exists(df_today_tmppath):
            if round(time.time() - os.path.getmtime(df_today_tmppath)) < 600:  # 据创建时间小于10分钟读取本地文件
                print(f'检测到本地临时最新行情文件，读取并合并股票数据')
                df_today = pd.read_pickle(df_today_tmppath)
            else:
                df_today = func.get_tdx_lastestquote(stocklist)
                df_today.to_pickle(df_today_tmppath, compression=None)
        else:
            df_today = func.get_tdx_lastestquote(stocklist)
            df_today.to_pickle(df_today_tmppath, compression=None)
        return df_today
    else:
        try:
            os.remove(df_today_tmppath)
        except FileNotFoundError:
            pass
        return None




# 主程序开始
if __name__ == '__main__':
    mark_day = QA_util_today_str()
    # mark_day = '2022-09-04'
    if QA_util_if_trade(mark_day):
        if QA_util_get_last_day(mark_day) == 'wrong date':
            to_date = QA_util_get_real_date(mark_day)
        else:
            to_date = QA_util_get_last_day(mark_day)
    else:
        mark_day = QA_util_get_real_date(mark_day)
        to_date = QA_util_get_last_day(mark_day)

    # if 'single' in sys.argv[1:]:
    #     print(f'检测到参数 single, 单进程执行')
    # else:
    #     print(f'附带命令行参数 single 单进程执行(默认多进程)')
    # starttime = time.time()
    codes = make_stocklist()
    print(f'共 {len(codes)} 只候选股票')
    # endtime= time.time()
    # costtime = endtime - starttime
    # print(f'共 {len(stocklist)} 只候选股票,耗时 {costtime} s')
    # dicttemp = load_dict_stock(stocklist,end_date=to_date )
    # print(dicttemp.head(10))
    # gbbqload()
    df_gbbq = pd.read_csv('E:/TDXdata' + os.sep + 'gbbq.csv', encoding='gbk', dtype={'code': str})
    # df_gbbq_qa = QA_fetch_stock_xdxr(codes).reset_index(drop=True).fillna(0)

    HS300_signal = HS300_SIGNAL()

    # df_today = func.get_tdx_lastestquote(stocklist)
    df_today = get_df_today(codes)
    # print(df_today.head(5))


    starttime_tick = time.time()
    # stocklist = runcelue1(codes,df_today,runtype='single')
    print(f'开始执行策略1(mode=fast)')
    if 'single' in sys.argv[1:]:
        stocklist = run_celue1(codes, df_today)
    else:    #多进程需要放在main里跑
        t_num = os.cpu_count() - 2  # 进程数 读取CPU逻辑处理器个数
        div, mod = int(len(codes) / t_num), len(codes) % t_num
        freeze_support()  # for Windows support
        tqdm.set_lock(RLock())  # for managing output contention
        p = Pool(processes=t_num, initializer=tqdm.set_lock, initargs=(tqdm.get_lock(),))
        pool_result = []  # 存放pool池的返回对象列表

        for i in range(0, t_num):
            # div = int(len(stocklist) / t_num)
            # mod = len(stocklist) % t_num

            if i + 1 != t_num:
                # print(i, i * div, (i + 1) * div)
                pool_result.append(p.apply_async(run_celue1, args=(codes[i * div:(i + 1) * div], df_today, i,)))
            else:
                # print(i, i * div, (i + 1) * div + mod)
                pool_result.append(p.apply_async(run_celue1, args=(codes[i * div:(i + 1) * div + mod], df_today, i,)))

        # print('Waiting for all subprocesses done...')
        p.close()
        p.join()

        stocklist = []
        # 读取pool的返回对象列表。i.get()是读取方法。拼接每个子进程返回的df
        for i in pool_result:
            stocklist = stocklist + i.get()
    print(f'策略1执行完毕，已选出 {len(stocklist):>d} 只股票 用时 {(time.time() - starttime_tick):>.2f} 秒')
    print(stocklist)

    print(f'开始执行策略2')
    # 如果没有df_today
    if '09:00:00' < time.strftime("%H:%M:%S", time.localtime()) < '16:00:00' and 'df_today' not in dir():
        df_today = func.get_tdx_lastestquote(stocklist)  # 获取当前最新行情

    starttime_tick = time.time()
    if 'single' in sys.argv[1:]:
    # if runtype == 'single':
        stocklist = run_celue2(stocklist, HS300_signal, df_gbbq, df_today)
    else:
        # 由于df_dict字典占用超多内存资源，导致多进程效率还不如单进程
        t_num = os.cpu_count() - 2  # 进程数 读取CPU逻辑处理器个数
        freeze_support()  # for Windows support
        tqdm.set_lock(RLock())  # for managing output contention
        p = Pool(processes=t_num, initializer=tqdm.set_lock, initargs=(tqdm.get_lock(),))
        pool_result = []  # 存放pool池的返回对象列表
        for i in range(0, t_num):
            div = int(len(stocklist) / t_num)
            mod = len(stocklist) % t_num
            if i + 1 != t_num:
                # print(i, i * div, (i + 1) * div)
                pool_result.append(p.apply_async(run_celue2, args=(stocklist[i * div:(i + 1) * div], HS300_signal, df_gbbq, df_today, i,)))
            else:
                # print(i, i * div, (i + 1) * div + mod)
                pool_result.append(p.apply_async(run_celue2, args=(stocklist[i * div:(i + 1) * div + mod], HS300_signal, df_gbbq, df_today, i,)))

        # print('Waiting for all subprocesses done...')
        p.close()
        p.join()

        stocklist = []
        # 读取pool的返回对象列表。i.get()是读取方法。拼接每个子进程返回的df
        for i in pool_result:
            stocklist = stocklist + i.get()