from celery_tasks.main import app
from libs.yuntongxun.sms import CCP
from utils import constants


@app.task()
def send_sms_code(mobile, sms_code):
    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES], constants.SMS_SEND_TEMPLATE)
