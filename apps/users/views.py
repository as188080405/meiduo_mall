import re

from django import http
from django.contrib.auth import login
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_redis import get_redis_connection

# Create your views here.
from django.urls import reverse
from django.views import View

from apps.users.models import User


class RegisterView(View):

    # 获取注册页面
    def get(self, request):
        return render(request, 'register.html')

    # 完成注册功能
    def post(self, request):

        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        cli_sms_code = request.POST.get('sms_code')
        print('参数接收:', username, password, password2, mobile, allow, cli_sms_code)

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow, cli_sms_code]):
            return http.HttpResponseBadRequest('缺少必填参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{5,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')
        if not re.match(r'\d{6}', cli_sms_code):
            return http.HttpResponseBadRequest('短信验证码错误')
        try:
            # 验证短信验证码
            redis_conn = get_redis_connection('code')
            # 获取redis中的短信验证码
            redis_sms_code = redis_conn.get('sms_%s' % mobile)
            # 判断redis中的短信验证码，是否过期
            if redis_sms_code is None:
                return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
            # 判断用户输入和reids中的短信验证码是否一致
            if redis_sms_code.decode() != cli_sms_code:
                return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})
            # 注册的用户数据存入数据库
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_msg': '注册失败!'})
        # 记住当前注册用户，免登录
        login(request, user)
        # 响应网站首页
        return redirect(reverse('contents:index'))


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')
