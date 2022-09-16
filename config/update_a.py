#!/usr/local/bin/python

#coding :utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2016-2018 yutiansut/QUANTAXIS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""对应于save x
"""
from QUANTTOOLS.QAStockETL import (QA_SU_save_stock_divyield_day,QA_SU_save_report_calendar_day)
from QUANTTOOLS.QAStockETL import (QA_SU_save_interest_rate,QA_etl_stock_calendar,
                                    QA_etl_stock_divyield,QA_SU_save_usstock_list_day)





if __name__ == '__main__':
    print("write divyield data into sqldatabase")
    QA_SU_save_usstock_list_day()
    #QA_SU_save_interest_rate() #tushare 已不能从sina获取该数据。baostock的query_deposit_rate_data接口，也只能获取到15年前的数据
    QA_SU_save_stock_divyield_day()    #https://stock.jrj.com.cn/report/js/sz/2022-06-30.js?ts=1662081936
    QA_etl_stock_divyield("all")
    print("done")
    print("write calendar data into sqldatabase")
    QA_SU_save_report_calendar_day()     #https://app.jrj.com.cn/jds/data_ylj.php?cid=1002&_pd=&_pd2=&_pid=2022-06-30&ob=2&od=d&page=1&psize=2000&vname=plsj
    QA_etl_stock_calendar()
    print("done")
