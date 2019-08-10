# name: 异步任务别名
from celery_tasks.main import celery_app
from meiduo_mall.lib.yuntongxun.sms import CCP
#TODO from verifications import constants


@celery_app.task(name='ccp_send_sms_code')
def ccp_send_sms_code(self, mobile, sms_code):
    '''发送短信异步任务'''

    # TODO send_ret = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.)

    return send_ret