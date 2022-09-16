from QUANTAXIS.QAUtil.QASetting import QA_Setting

QASETTING = QA_Setting()

QAPRO_ID = QASETTING.get_config('WECHAT','QAPRO_ID')
CORPID = QASETTING.get_config('WECHAT','CORPID')
CORPSECRET = QASETTING.get_config('WECHAT','CORPSECRET')
AGENTID = QASETTING.get_config('WECHAT','AGENTID')
smtpserver = QASETTING.get_config('EMAIL','smtpserver')
smtpport = QASETTING.get_config('EMAIL','smtpport')
msg_from = QASETTING.get_config('EMAIL','msg_from')        #发送方邮箱
passwd = QASETTING.get_config('EMAIL','passwd')            #填入发送方邮箱的授权码
msg_to = QASETTING.get_config('EMAIL','msg_to').split(',') #收件人邮箱