#coding=utf-8

from QUANTTOOLS.Model.StockModel.StrategyXgboost import QAStockXGBoost
from QUANTTOOLS.Model.StockModel.StrategyXgboostHedge import QAStockXGBoostHedge
from QUANTTOOLS.Model.IndexModel.IndexXGboost import QAIndexXGBoost
from .setting import working_dir, data_set, datareal_set
from QUANTTOOLS.Market.MarketTools.train_tools import prepare_train, start_train, save_report, load_data, prepare_data

def train(date, working_dir=working_dir):
    stock_model = QAStockXGBoost()

    stock_model = load_data(stock_model, date, k = 3, start = "-01-01", shift=5, norm_type=None)

    stock_model = prepare_data(stock_model, date, col = 'TARGET5', k = 3, start = "-01-01", shift=5)

    #stock_model = prepare_train(stock_model, date, col = 'TARGET5', k = 3, start = "-01-01", shift=5)

    other_params = {'learning_rate': 0.1, 'n_estimators': 200, 'max_depth': 5, 'min_child_weight': 1, 'seed': 1,
                    'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0, 'reg_alpha': 0, 'reg_lambda': 1}

    stock_model = start_train(stock_model, data_set, other_params, 0, 0.99)
    save_report(stock_model, 'stock_xg', working_dir)

    #stock_model = start_train(stock_model, datareal_set,  other_params, 0, 0.99)
    #save_report(stock_model, 'stock_xg_real', working_dir)

    hedge_model = QAStockXGBoostHedge()
    hedge_model = load_data(hedge_model, date, k = 3, start = "-01-01", shift=1, norm_type=None)

    hedge_model = prepare_data(hedge_model, date, col = 'TARGET', k = 3, start = "-01-01", shift=1)

    other_params = {'learning_rate': 0.1, 'n_estimators': 200, 'max_depth': 5, 'min_child_weight': 1, 'seed': 1,
                    'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0, 'reg_alpha': 0, 'reg_lambda': 1}

    hedge_model = start_train(hedge_model, datareal_set, other_params, 0, 0.99)
    save_report(hedge_model, 'hedge_xg', working_dir)

def train_hedge(date, working_dir=working_dir):
    hedge_model = QAStockXGBoostHedge()
    hedge_model = load_data(hedge_model, date, k = 3, start = "-01-01", shift=5, norm_type=None)

    hedge_model = prepare_data(hedge_model, date, col = 'TARGET', k = 3, start = "-01-01", shift=1)

    other_params = {'learning_rate': 0.1, 'n_estimators': 200, 'max_depth': 5, 'min_child_weight': 1, 'seed': 1,
                    'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0, 'reg_alpha': 0, 'reg_lambda': 1}

    hedge_model = start_train(hedge_model, datareal_set, other_params, 0, 0.99)
    save_report(hedge_model, 'hedge_xg', working_dir)

def train_index(date, working_dir=working_dir):
    index_model = QAIndexXGBoost()
    index_model = prepare_train(index_model, date, col = 'INDEX_TARGET',k = 3, start = "-01-01", shift=5)

    other_params = {'learning_rate': 0.1, 'n_estimators': 200, 'max_depth': 5, 'min_child_weight': 1, 'seed': 1,
                    'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0, 'reg_alpha': 0, 'reg_lambda': 1}

    index_model = start_train(index_model, None, other_params, 0, 0.99)
    save_report(index_model, 'index_xg', working_dir)