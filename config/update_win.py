from QUANTAXIS.QASU.main import (QA_SU_save_stock_block,QA_SU_save_stock_list)
from QUANTAXIS.QASU.save_tdx import QA_SU_save_single_stock_day
from QUANTTOOLS.QAStockETL import (QA_etl_stock_list,QA_SU_save_stock_info_tushare, QA_etl_stock_info, QA_etl_stock_xdxr, QA_etl_stock_day, QA_etl_stock_financial,
                                   QA_etl_stock_block, QA_etl_process_financial_day,QA_etl_stock_financial_wy,
                                   QA_SU_save_stock_xdxr, QA_SU_save_stock_info,QA_SU_save_stock_financial_wy_day,
                                   QA_SU_save_stock_fianacial_percent_day, QA_util_process_stock_financial,
                                   QA_SU_save_stock_fianacial_momgo, QA_SU_save_fianacialTTM_momgo,
                                   QA_SU_save_stock_industryinfo, QA_SU_save_stock_day,
                                   QA_SU_save_single_stock_xdxr,QA_SU_save_stock_aklist,
                                   QA_SU_save_stock_neutral_day)
from QUANTTOOLS.QAStockETL import (QA_etl_stock_financial_day,
                                   QA_etl_stock_financial_percent_day)
from QUANTAXIS.QASU.main import (QA_SU_save_financialfiles_fromtdx)
from QUANTTOOLS.QAStockETL.Check import (check_stock_day, check_stock_fianacial, check_stock_adj, check_stock_finper,
                                         check_sinastock_day, check_sinastock_adj,check_stock_code, check_stock_quant,
                                         check_wy_financial, check_tdx_financial, check_ttm_financial)
from  QUANTAXIS.QAUtil import QA_util_today_str,QA_util_if_trade
from QUANTTOOLS.QAStockETL import QA_etl_stock_shares,QA_SU_save_stock_shares_sina_day,QA_SU_save_report_calendar_day,QA_SU_save_stock_divyield_day,QA_etl_stock_shares
import time

if __name__ == '__main__':
    mark_day = QA_util_today_str()
    if QA_util_if_trade(mark_day):
        QA_SU_save_stock_industryinfo()
        # QA_SU_save_stock_shares_sina_day()  # sina 爬取数据存储在mongo stock_shares，耗时很久
        #QA_etl_stock_shares()
        # QA_SU_save_report_calendar_day()    # jrj 爬取数据存储在mongo report_calendar
        # QA_SU_save_stock_divyield_day()     # jrj 爬取数据存储在mongo stock_divyield
        # QA_etl_stock_list()
        QA_etl_stock_info()        #数据来源于QA_SU_save_stock_industryinfo()存储的stock_industry
        # QA_etl_stock_xdxr(type = "all")
        # QA_etl_stock_calendar('all')
        # QA_etl_stock_divyield('all')
        QA_etl_stock_day('day',mark_day)
        QA_etl_stock_block()

        # print("done")
        # print("run financial data into sqldatabase")
        #
        res = check_tdx_financial(mark_day)
        if res is None or res > 0:
            QA_SU_save_financialfiles_fromtdx()
            QA_etl_stock_financial('all')

        res = check_wy_financial(mark_day)
        while res is None or res > 0:
            QA_SU_save_stock_financial_wy_day()
            res = check_wy_financial(mark_day)
        #
        # QA_etl_stock_financial_wy('all')
        # print("done")
        # print("processing quant data in sqldatabase")
        QA_util_process_stock_financial()

        res = check_ttm_financial(mark_day)
        if res is None or res > 20:
            QA_SU_save_fianacialTTM_momgo()
            check_ttm_financial(mark_day)