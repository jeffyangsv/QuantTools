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

from QUANTAXIS.QASU.main import (QA_SU_save_stock_block,QA_SU_save_stock_list,QA_SU_save_financialfiles_fromtdx)
from QUANTAXIS.QASU.save_tdx import QA_SU_save_single_stock_day
from QUANTTOOLS.QAStockETL import (QA_etl_stock_list,QA_SU_save_stock_info_tushare, QA_etl_stock_info, QA_etl_stock_xdxr, QA_etl_stock_day, QA_etl_stock_financial,
                                   QA_etl_stock_block, QA_etl_process_financial_day,QA_etl_stock_financial_wy,
                                   QA_SU_save_stock_xdxr, QA_SU_save_stock_info,QA_SU_save_stock_financial_wy_day,
                                   QA_SU_save_stock_fianacial_percent_day, QA_util_process_stock_financial,
                                   QA_SU_save_stock_fianacial_momgo, QA_SU_save_fianacialTTM_momgo,
                                   QA_SU_save_stock_industryinfo, QA_SU_save_stock_day,QA_SU_save_stock_delist,
                                   QA_SU_save_single_stock_xdxr,QA_SU_save_stock_aklist,QA_SU_save_single_stock_day_from_akshare,
                                   QA_SU_save_stock_neutral_day,QA_etl_stock_financial_day,QA_etl_stock_financial_percent_day)

from QUANTTOOLS.QAStockETL.Check import (check_stock_day, check_stock_fianacial, check_stock_adj, check_stock_finper,
                                         check_sinastock_day, check_sinastock_adj,check_stock_code, check_stock_quant,check_akstock_day,
                                         check_wy_financial, check_tdx_financial, check_ttm_financial)
from  QUANTAXIS.QAUtil import QA_util_today_str,QA_util_if_trade
import time

if __name__ == '__main__':
    mark_day = QA_util_today_str()
    if QA_util_if_trade(mark_day):
        #
        # try:
        #     QA_SU_save_stock_aklist()
        # except:
        #     pass
        # QA_SU_save_stock_list('tdx')
        QA_SU_save_stock_info_tushare()
        QA_SU_save_stock_industryinfo()
        QA_SU_save_stock_delist()
        # print("download day data")
        #
        # res = check_stock_day(mark_day)
        # if res is None or len(res[1]) > 500:
        #     QA_SU_save_stock_day()
        #
        res = check_sinastock_day(mark_day)
        while res is None or len(res[1]) > 0:
            for i in res[0] + res[1]:
                QA_SU_save_single_stock_day(i)
            res = check_sinastock_day(mark_day)

        res = check_akstock_day(mark_day)   #与akshare数据对比
        while res is None or len(res[1]) > 0:
            for i in res[0] + res[1]:
                QA_SU_save_single_stock_day(i)
            res = None         #补录一遍后退出循环

        res = check_akstock_day(mark_day)
        while res is None or len(res[1]) > 0:
            for i in res[0] + res[1]:
                QA_SU_save_single_stock_day_from_akshare(i)
            res = check_akstock_day(mark_day)

        # QA_SU_save_stock_block('tdx')
        #
        # res = check_stock_adj(mark_day)
        # if res is None or len(res[1]) > 500:
        #     QA_SU_save_stock_xdxr()

        #注释这部分，
        # res = check_sinastock_adj(mark_day)
        # # while res is None or len(res[1]) > 5:
        # while len(res[1]) > 5:
        #     for i in res[0] + res[1]:
        #         QA_SU_save_single_stock_xdxr(i)
        #     res = check_sinastock_adj(mark_day)

        # print("done")
        # print("write data into sqldatabase")

        QA_etl_stock_list()        #mongo stock_list 转存 oracle stock_list
        QA_etl_stock_info()        #数据来源于QA_SU_save_stock_industryinfo()存储的stock_industry
        QA_etl_stock_xdxr(type = "all")    #mongo stock_xdxr 转存 oracle stock_xdxr
        QA_etl_stock_day('day',mark_day)   #mongo stock_day 转存 oracle stock_market_day
        QA_etl_stock_block()               #mongo stock_block 转存 oracle stock_block

        # print("done")
        # print("run financial data into sqldatabase")
        #
        res = check_tdx_financial(mark_day)
        if res is None or res > 0:
            QA_SU_save_financialfiles_fromtdx()   # 从tdx获取财务数据保存在mongo financial
            QA_etl_stock_financial('all')         #mongo financial 转存 oracle stock_financial

        res = check_wy_financial(mark_day)
        while res is None or res > 0:
            QA_SU_save_stock_financial_wy_day()   #mongo 存储 stock_financial_wy
            res = check_wy_financial(mark_day)

        QA_etl_stock_financial_wy('all')       #mongo stock_financial_wy 转存 oracle stock_financial_wy
        # print("done")
        # print("processing quant data in sqldatabase")
        QA_util_process_stock_financial()  #oracle根据stock_financial和stock_financial_wy的数据创建 table stock_financial_TTM;根据stock_financial_TTM  stock_calendar stock_info 的数据生成stock_financial_analysis

        QA_etl_process_financial_day('day',mark_day)   #由 oracle 的 stock_market_day stock_shares stock_financial_analysis 3表生成 stock_analysis_data
        # print("done")
        # print("write quant data into mongodb")
        #
        res = check_stock_fianacial(mark_day)
        while res is None or len(res[1]) > 360:
            QA_SU_save_stock_fianacial_momgo(mark_day,mark_day)    #由oracle的stock_analysis_data 生成mongo 的表 stock_financial_analysis
            res = check_stock_fianacial(mark_day)

        res = check_stock_finper(mark_day)
        while res is None or len(res[1]) > 360:
            QA_SU_save_stock_fianacial_percent_day(start_date = mark_day, end_date = mark_day)   #根据 mongo 表 stock_financial_analysis 生成 mongo 表 stock_financial_percent
            res = check_stock_finper(mark_day)
        #
        QA_etl_stock_financial_day(mark_day, mark_day)                           #根据 mongo 表 stock_financial_analysis 生成  oracle 表 stock_quant_financial
        QA_etl_stock_financial_percent_day(mark_day, mark_day)                   #根据 mongo 表 stock_financial_percent 生成  oracle 表 stock_quant_financial_percent

        QA_SU_save_stock_info()
