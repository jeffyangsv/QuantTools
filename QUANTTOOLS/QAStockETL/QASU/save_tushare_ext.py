#tushare的get_stock_basics接口已不能使用，导致QUANTAXIS.QASU.save_tushare 中 QA_SU_save_stock_info_tushare无效
#tushare bak_basic获取的数据相同，字段不同，这里做兼容

import json
import time

from QUANTAXIS.QAUtil import (
    QA_util_get_real_date,
    QA_util_today_str,
    QA_util_get_last_day,
    QA_util_if_trade
)
from QUANTAXIS.QAUtil.QASetting import DATABASE
from QUANTAXIS.QAFetch.QATushare import get_pro


def QA_SU_save_stock_info_tushare(client=DATABASE):
    '''
        获取 股票的 基本信息，包含股票的如下信息

        code,代码
        name,名称
        industry,所属行业
        area,地区
        pe,市盈率
        outstanding,流通股本(亿)
        totals,总股本(亿)
        totalAssets,总资产(万)
        liquidAssets,流动资产
        fixedAssets,固定资产
        reserved,公积金
        reservedPerShare,每股公积金
        esp,每股收益
        bvps,每股净资
        pb,市净率
        timeToMarket,上市日期
        undp,未分利润
        perundp, 每股未分配
        rev,收入同比(%)
        profit,利润同比(%)
        gpr,毛利率(%)
        npr,净利润率(%)
        holders,股东人数

        add by tauruswang

    在命令行工具 quantaxis 中输入 save stock_info_tushare 中的命令
    :param client:
    :return:
    '''


    pro = get_pro()
    mark_day = QA_util_today_str()
    if QA_util_if_trade(mark_day):
        if QA_util_get_last_day(mark_day) == 'wrong date':
            to_date = QA_util_get_real_date(mark_day)
        else:
            to_date = QA_util_get_last_day(mark_day)
    else:
        mark_day = QA_util_get_real_date(mark_day)
        to_date = QA_util_get_last_day(mark_day)
    df = pro.bak_basic(trade_date = time.strftime("%Y%m%d",time.strptime(to_date, "%Y-%m-%d")))
    df['ts_code'] = df['ts_code'].apply(lambda x: x[:6])
    df.columns = ['trade_date', 'code', 'name', 'industry', 'area', 'pe',
       'outstanding', 'totals', 'totalAssets', 'liquidAssets',
       'fixedAssets', 'reserved', 'reservedPerShare', 'esp', 'bvps', 'pb',
       'timeToMarket', 'undp', 'perundp', 'rev', 'profit', 'gpr', 'npr',
       'holders']
    print(" Get stock info from tushare,stock count is %d" % len(df))
    coll = client.stock_info_tushare
    client.drop_collection(coll)
    json_data = json.loads(df.reset_index().to_json(orient='records'))
    # print(pd.DataFrame(json_data))
    coll.insert_many(json_data)
    print(" Save data to stock_info_tushare collection， OK")