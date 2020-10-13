
from .setting import working_dir, percent, exceptions
from .concat_predict import concat_predict,concat_predict_real,concat_predict_hedge
from QUANTTOOLS.Market.MarketTools import trading_base

def trading(trading_date, func = concat_predict, model_name = 'stock_xg', file_name = 'prediction', percent = percent, account= 'name:client-1', working_dir = working_dir, exceptions = exceptions):
    trading_base(trading_date, func, model_name, file_name, percent = percent, account= account, working_dir = working_dir, exceptions = exceptions)

def trading_real(trading_date, func = concat_predict_real, model_name = 'stock_xg_real', file_name = 'prediction_real', percent = percent, account= 'name:client-1', working_dir = working_dir, exceptions = exceptions):
    trading_base(trading_date, func, model_name, file_name, percent = percent, account= account, working_dir = working_dir, exceptions = exceptions)

def trading_hedge(trading_date, func = concat_predict_hedge, model_name = 'hedge_xg', file_name = 'prediction_hedge', percent = percent, account= 'name:client-1', working_dir = working_dir, exceptions = exceptions):
    trading_base(trading_date, func, model_name, file_name, percent = percent, account= account, working_dir = working_dir, exceptions = exceptions)

if __name__ == '__main__':
    pass
