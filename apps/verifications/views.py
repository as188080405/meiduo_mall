import logging
from random import randint
from django.shortcuts import render

# Create your views here.
from django.views import View

from celery_tasks.sms.tasks import send_sms_code
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http

from libs.yuntongxun.sms import CCP
from utils import constants
from utils.response_code import RETCODE

logger = logging.getLogger('Django')


class ImageCodeView(View):

    def get(self, request, uuid):
        # 插件生成图片/验证码
        text, image = captcha.generate_captcha()
        # 获取redis链接
        redis_conn = get_redis_connection('code')
        # 将uuid作为key，生产的图片验证码文本做为value。存入redis
        redis_conn.setex('img_%s' % uuid, 120, text)
        # 返回image给html，并告诉浏览器用图片的格式解析
        return http.HttpResponse(image, content_type='image/jpeg')


class SMSCodeView(View):
    """ 短信发送 """
    def get(self, request, mobile):
        # 获取请求参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 判断请求参数是否为空
        if not all([image_code, uuid]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})
        try:
            # redis链接
            redis_conn = get_redis_connection('code')
            # 查询是否发送过短信，是否是重复发送
            sms_falg = redis_conn.get('sms_falg_%s' % mobile)
            # 重复发送响应异常提示
            if sms_falg:
                return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '短信发送过于频繁'})
            # 获取前端生成的图片验证码UUID
            redis_image_code = redis_conn.get('img_%s' % uuid)
            # 获取图片验证码
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.error('redis验证码异常：' + e)
        # 判断图片验证码是否存在，不存在提示异常
        if redis_image_code is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
        # 判断redis中的图片验证码，和用户传递的是否相同
        if image_code.lower() != redis_image_code.decode().lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})
        # 随机生成6位短信发送的验证码
        sms_code = '%06d' % randint(0, 999999)
        # 将短信验证码存入redis
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 为发送过信息，设置开关为1，避免重复频繁发送短信验证（前面有判断，为1代表发送过）
        redis_conn.setex('sms_falg_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, 1)
        # 发送短信
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES], constants.SMS_SEND_TEMPLATE)
        # 响应成功信息
        send_sms_code.delay(mobile, sms_code)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '短信发送成功'})
