import logging
import strategyease_sdk
from QUANTTOOLS.Message.message_func.qaemail import send_email
from QUANTTOOLS.Message.message_func.wechat import send_actionnotice
from  QUANTAXIS.QAUtil import QA_util_today_str,QA_util_if_trade

if __name__ == '__main__':
    mark_day = QA_util_today_str()
    if QA_util_if_trade(mark_day):
        logging.basicConfig(level=logging.DEBUG)
        client = strategyease_sdk.Client(host='132.232.89.97', port=8888, key='123456')
        account1='name:client-1'

        try:
            account_info = client.get_account(account1)
            print(account_info)
        except:
            send_email('错误报告', '云服务器错误,请检查', 'date')
            send_actionnotice('自动打新',
                              '错误报告:{}'.format(mark_day),
                              '云服务器错误,请检查',
                              direction = 'HOLD',
                              offset='HOLD',
                              volume=None
                              )
        #to_do
        #自动打新
        try:
            client.purchase_new_stocks(account1)
            send_email('每日打新', '打新成功', 'date')
            send_actionnotice('自动打新',
                              '报告:{}'.format(mark_day),
                              '自动打新完成,请查收结果',
                              direction = 'BUY',
                              offset='OPEN',
                              volume=None
                              )
        except:
            print('打新失败')
            send_email('错误报告', '打新失败', 'date')




