import akshare as ak
import datetime
import pandas as pd
from  QUANTAXIS.QAUtil import (QA_util_today_str,QA_util_date_stamp,QA_util_log_info,
                               )

# pd.set_option('display.max_rows', 5000)
# pd.set_option('display.max_columns', 100)
# pd.set_option('display.width', 300)

def QA_fetch_get_stock_day_from_ak(code, start_date = None, end_date = None, if_fq='00',frequence='day'):
    # data = QA_fetch_get_stock_half_realtime_from_akshare()[['open', 'close', 'high', 'low', 'volume', 'amount', 'date', 'code', 'date_stamp']].rename(columns={'volume': 'vol'})
    # data = data[data["code"] == str(code)[0:6]]
    if start_date is None:
        start_date = QA_util_today_str()
    if end_date is None:
        end_date = QA_util_today_str()
    start_date = datetime.datetime.strptime(str(start_date)[0:10], "%Y-%m-%d").strftime("%Y%m%d")
    end_date = datetime.datetime.strptime(str(end_date)[0:10], "%Y-%m-%d").strftime("%Y%m%d")

    if if_fq in ['02', 'hfq']:
        adjust="hfq"
    elif if_fq in ['01', 'qfq']:
        adjust="qfq"
    else:
        adjust = ""

    if frequence in ['day', 'd', 'D', 'DAY', 'Day']:
        period = "daily"
    elif frequence in ['w', 'W', 'Week', 'week']:
        period = 'weekly'
    elif frequence in ['month', 'M', 'm', 'Month']:
        period = 'monthly'
    else:
        print('CURRENTLY ONLY SUPPORT Day week Month')
        return None
    try:
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=str(code)[0:6], period=period, start_date=start_date, end_date=end_date,
                                            adjust=adjust)
        res = stock_zh_a_hist_df[['开盘', '收盘', '最高', '最低', '成交量', '成交额', '日期']]
        res = res.reset_index(drop=True).rename(columns={# '昨收': 'prev_close',
                                                         '开盘': 'open',
                                                         '收盘': 'close',
                                                         '最高': 'high',
                                                         '最低': 'low',
                                                         '成交量': 'vol',
                                                         '成交额': 'amount',
                                                          # '代码': 'code',
                                                          '日期': 'date',

        }).set_index('date',drop=False)

        # res.insert(1, 'date', pd.to_datetime(date))
        res['code'] = str(code)[0:6]
        res[['open', 'close', 'high', 'low', 'vol', 'amount']] = res[
            ['open', 'close', 'high', 'low', 'vol', 'amount']].apply(pd.to_numeric)
        # res['avg_price'] = res['amount'] / res['volume'] / 100
        res = res[res.vol > 0]
        res['date_stamp'] = res['date'].apply(lambda x: QA_util_date_stamp(str(x)[0:10]))

        return(res)
    except:
        QA_util_log_info(
            '##JOB Now Get Stock data from akshare Failed ============== {deal_date} to {to_date} '.format(deal_date=start_date,
                                                                                             to_date=end_date))
        return None


if __name__ == '__main__':
    # stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol='000922', period="daily", start_date="20220915", end_date='20220915',
    #                                             adjust="")
    stock_zh_a_hist_df = QA_fetch_get_stock_day_from_ak('000922')
    print(stock_zh_a_hist_df)


