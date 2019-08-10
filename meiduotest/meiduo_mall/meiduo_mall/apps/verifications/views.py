import random

from django.contrib.auth import logout


from django.views import View
from django import http
from django_redis import get_redis_connection

from meiduo_mall.lib.captcha.captcha import captcha
from meiduo_mall.lib.yuntongxun.sms import CCP
from meiduo_mall.utils.response_code import RETCODE
from verifications import constants


class ImageCodeView(View):
    '''图形验证码'''

    def get(self, request, uuid):
        # SDK生成图形验证码
        name, text, image_code = captcha.generate_captcha()
        # 连接reids
        redis_conn = get_redis_connection('verify_codes')
        # 将图形验证码字符串储存到reids数据库
        redis_conn.setex(uuid, constants.IMAGE_CODE_EXPIRE, text)
        # 响应

        return http.HttpResponse(image_code, content_type='image/png')


class SMSCodeView(View):
    '''发短信验证码'''

    def get(self, request, mobile):
        # 接收前段传入的数据
        query_dict = request.GET
        image_code_client = query_dict.get('image_code')
        uuid = query_dict.get('uuid')

        # 校验

        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')

        # 将redis中的图形验证码获取来
        image_code_server_bytes = redis_conn.get(uuid)
        # 图形验证码从redis获取出来之后就从redis数据库删除（验证码填一次没对就gg）
        redis_conn.delete(uuid)
        # 判断redis中是否获取到图形验证码（判断是否过期）
        if image_code_server_bytes is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码过期'})
        image_code_server = image_code_server_bytes.decode()
        # 从redis获取出来的数据注意类型问题

        # 验证码的大小写问题
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '图形验证码输入错误'})

        # 发送短信验证码

        # 生成随机数作为短信验证码
        sms_code = '%06d' % random.randint(0,999999)
        # 将短信验证码缓存到redis
        redis_conn.setex('sms_code%s' % mobile, constants.SMS_CODE_EXPIRE, sms_code)

        # 用熔炼云平台发送短信
        CCP().send_template_sms(mobile, [sms_code,5], 1)

        #响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'blablabla'}) # 这里不会返回错误，所以瞎姬霸写


