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
from QUANTTOOLS.QAStockETL.QAFetch import QA_fetch_stock_all,QA_fetch_stock_om_all,QA_fetch_stock_real,QA_fetch_code_new,QA_fetch_stock_industryinfo_bytdxhy,QA_fetch_get_stock_half_realtime
from QUANTAXIS.QAFetch.QAQuery_Advance import (QA_fetch_stock_day_adv,QA_fetch_index_day_adv)
from QUANTAXIS.QAFetch.QAQuery import (QA_fetch_stock_xdxr)
from QUANTAXIS import QA_fetch_stock_block,QA_fetch_index_list_adv,QA_fetch_stock_adj,QA_fetch_get_index_list
import pytdx.reader.gbbq_reader
from  QUANTAXIS.QAUtil import (QA_util_today_str,QA_util_if_trade,QA_util_add_months,QA_util_date_int2str,DATABASE,
                               QA_util_get_real_date,QA_util_log_info,QA_util_date_stamp,
                               QA_util_get_next_day,
                               QA_util_get_last_day,
                               QA_util_get_trade_range
                               )
from QUANTTOOLS.Message.message_func.wechat import send_actionnotice


pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 300)


# mark_day = '2022-09-14'
# res = check_stock_base(func1 = QA_fetch_stock_day, func2 = QA_fetch_stock_half_realtime, mark_day = mark_day, title = 'Stock Day sina')
# print(res)
# import tushare as ts
# pro = ts.pro_api()
# df = pro.daily(trade_date='20220914')
#
# print(df.ts_code.head(10))
# import easyquotation
# date = QA_util_today_str()
# code = list(QA_fetch_stock_all()['code'])
# source = 'sina'
# quotation = easyquotation.use(source)
# res = pd.DataFrame(quotation.stocks(code)).T[['date', 'open', 'high', 'low', 'now', 'turnover', 'volume', 'close']]
# res = res.reset_index().rename(columns={'index': 'code',
#                                         'close': 'prev_close',
#                                         'now': 'close',
#                                         'turnover': 'volume',
#                                         'volume': 'amount'})
# res['date'] = pd.to_datetime(res['date'])
# res[['open', 'high', 'low', 'close', 'volume', 'amount', 'prev_close']] = res[
#     ['open', 'high', 'low', 'close', 'volume', 'amount', 'prev_close']].apply(pd.to_numeric)
# res['avg_price'] = res['amount'] / res['volume']
# res = res[res.volume > 0]
# res = res[res.date == date]
# res['date_stamp'] = res['date'].apply(lambda x: QA_util_date_stamp(str(x)[0:10]))

# import akshare as ak
#
# stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
# res = stock_zh_a_spot_em_df[['代码', '今开', '最高', '最低', '最新价', '成交量', '成交额', '昨收']]
#
# res = res.reset_index(drop=True).rename(columns={'代码': 'code',
#                                         '昨收': 'prev_close',
#                                         '今开': 'open',
#                                         '最高':'high',
#                                         '最低':'low',
#                                         '最新价': 'close',
#                                         '成交量': 'volume',
#                                         '成交额': 'amount'})
# mark_day = QA_util_today_str()
# res.insert(1,'date',pd.to_datetime(mark_day))
# res[['open', 'high', 'low', 'close', 'volume', 'amount', 'prev_close']] = res[
#     ['open', 'high', 'low', 'close', 'volume', 'amount', 'prev_close']].apply(pd.to_numeric)
# res['avg_price'] = res['amount'] / res['volume']
# res = res[res.volume > 0]
# res['date_stamp'] = res['date'].apply(lambda x: QA_util_date_stamp(str(x)[0:10]))
# print(len(res))

from QUANTTOOLS.QAStockETL.QAFetch import (QA_fetch_get_stock_half_realtime,QA_fetch_stock_alpha_real,QA_fetch_stock_alpha101_real,
                                           QA_fetch_get_stock_half_realtime_from_akshare,QA_fetch_get_stock_day_from_ak)
from QUANTTOOLS.QAStockETL.Check import (check_stock_day, check_stock_fianacial, check_stock_adj, check_stock_finper,
                                         check_sinastock_day, check_sinastock_adj,check_stock_code, check_stock_quant,check_akstock_day,
                                         check_wy_financial, check_tdx_financial, check_ttm_financial)
from QUANTTOOLS.QAStockETL import QA_SU_save_single_stock_day_from_akshare
from QUANTAXIS.QASU.save_tdx import QA_SU_save_single_stock_day


def QA_fetch_stock_day(code, start, end):
    # mark_day = start
    # if QA_util_if_trade(mark_day):
    #     if QA_util_get_last_day(mark_day) == 'wrong date':
    #         start = QA_util_get_real_date(mark_day)
    #     else:
    #         start = QA_util_get_last_day(mark_day)
    # else:
    #     mark_day = QA_util_get_real_date(mark_day)
    #     start = QA_util_get_last_day(mark_day)
    # print(start,end)
    return(QA_fetch_stock_day_adv(code, start, end).data)

mark_day = QA_util_today_str()


# res = check_akstock_day(mark_day)
# while res is None or len(res[1]) > 0:
#     for i in res[0] + res[1]:
#         QA_SU_save_single_stock_day_from_akshare(i)
#     res = check_akstock_day(mark_day)

# code = list(QA_fetch_stock_all()['code'])
# data = QA_fetch_stock_day(code, mark_day, mark_day)
# print(data.head(5))
# data1 = data.reset_index().code.unique()

data = QA_fetch_get_stock_day_from_ak(
    str('600289'),
    QA_util_get_next_day(QA_util_get_real_date('1990-01-01')),
    '2022-09-15',
    '00'
)

print(data)