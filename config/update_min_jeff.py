from QUANTAXIS.QASU.main import (QA_SU_crawl_eastmoney, QA_SU_save_bond_day,
                                 QA_SU_save_bond_list, QA_SU_save_bond_min,
                                 QA_SU_save_etf_day, QA_SU_save_etf_list,
                                 QA_SU_save_etf_min, QA_SU_save_financialfiles,
                                 QA_SU_save_future_day,
                                 QA_SU_save_future_day_all,
                                 QA_SU_save_future_list, QA_SU_save_future_min,
                                 QA_SU_save_future_min_all,
                                 QA_SU_save_index_day, QA_SU_save_index_list,
                                 QA_SU_save_index_min,
                                 QA_SU_save_index_transaction,
                                 QA_SU_save_option_50etf_day,
                                 QA_SU_save_option_50etf_min,
                                 QA_SU_save_option_300etf_day,
                                 QA_SU_save_option_300etf_min,
                                 QA_SU_save_option_commodity_day,
                                 QA_SU_save_option_commodity_min,
                                 QA_SU_save_option_contract_list,
                                 QA_SU_save_option_day_all,
                                 QA_SU_save_option_min_all,
                                 QA_SU_save_report_calendar_day,
                                 QA_SU_save_report_calendar_his,
                                 QA_SU_save_single_bond_day,
                                 QA_SU_save_single_bond_min,
                                 QA_SU_save_single_etf_day,
                                 QA_SU_save_single_etf_min,
                                 QA_SU_save_single_future_day,
                                 QA_SU_save_single_future_min,
                                 QA_SU_save_single_index_day,
                                 QA_SU_save_single_index_min,
                                 QA_SU_save_single_stock_day,
                                 QA_SU_save_single_stock_min,
                                 QA_SU_save_stock_block, QA_SU_save_stock_day,
                                 QA_SU_save_stock_divyield_day,
                                 QA_SU_save_stock_divyield_his,
                                 QA_SU_save_stock_info,
                                 QA_SU_save_stock_info_tushare,
                                 QA_SU_save_stock_list, QA_SU_save_stock_min,
                                 QA_SU_save_stock_transaction,
                                 QA_SU_save_stock_xdxr)
from  QUANTAXIS.QAUtil import QA_util_today_str,QA_util_if_trade
from QUANTTOOLS.QAStockETL.QASU import (QA_SU_save_stock_1min,QA_SU_save_single_stock_1min,
                                        QA_SU_save_stock_aklist,QA_etl_stock_technical_hour)
from QUANTTOOLS import (QA_etl_stock_technical_day, QA_SU_save_stock_technical_index_day,QA_SU_save_stock_technical_index_his,
                                   QA_SU_save_stock_technical_week_day,QA_SU_save_stock_technical_week_his,
                                   QA_SU_save_stock_technical_month_day,QA_SU_save_stock_technical_month_his,QA_SU_save_stock_technical_hour_his,QA_SU_save_stock_technical_hour_day)

if __name__ == '__main__':
    mark_day = QA_util_today_str()
    if QA_util_if_trade(mark_day):
        QA_SU_save_stock_aklist()

        QA_SU_save_stock_min('tdx')
        QA_SU_save_index_min('tdx')
        QA_SU_save_etf_min('tdx')
        QA_SU_save_bond_min('tdx')
        QA_SU_save_stock_technical_hour_day(start_date = mark_day,  end_date = mark_day)
        QA_etl_stock_technical_hour(mark_day, mark_day)