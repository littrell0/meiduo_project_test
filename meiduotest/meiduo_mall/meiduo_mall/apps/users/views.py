import re

from django import http
from django.contrib.auth import login, authenticate, mixins
from django.db import DatabaseError
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse # TODO
# Create your views here.

from django.views import View

from meiduo_mall.utils.response_code import RETCODE
from users.models import User


class RegisterView(View):
    '''用户注册'''

    def get(self, request):
        '''提供注册界面'''
        return render(request, 'register.html')

    def post(self, request):
        '''实现用户注册'''
        # 接收请求体中表单数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        # 校验
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        # TODO: 短信验证码校验后期在补充

        # 新增用户记录
        # user = User.objects.create(
        #     username=username
        # )

        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 状态保持
        login(request, user)

        # # 保存注册数据
        # try:
        #     User.objects.create_user(username=username, password=password, mobile=mobile)
        # except DatabaseError:
        #     return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 跳转到首页
        return http.HttpResponse('注册成功，跳转到首页')


class UsernameCountView(View):
    '''判断用户名是否重复注册'''

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    '''判断手机号是否重复注册'''

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class LoginView(View):
    '''用户名登陆'''

    def get(self, request):
        '''提供登陆页面'''
        return render(request, 'login.html')

    def post(self, request):
        '''实现登陆逻辑'''
        # 接收参数
        query_dict = request.POST
        username = query_dict.get('username')
        password = query_dict.get('password')
        remembered = query_dict.get('remembered')

        # 认证登陆用户
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 实现状态保持
        login(request, user)
        # session 过期是时间设置为None，表示关闭浏览器为14天；cookie默认过气时间为7天
        # 设置状态保持的周期
        if remembered != 'on':
            # 没有记住用户：浏览器会话结束就过期，默认是两周
            request.session.set_expiry(0)

        # 响应登陆结果
        # 给cookie中设置username # TODO

        # TODO: 用户中心跳转 不写死
        return redirect(reverse('contents:index')) # TODO


class LogoutView(View):
    '''退出登陆'''

    def get(self, request):
        '''实现退出登陆逻辑'''
        # 清理session
        logout(request)
        # 退出登陆，重定向到登陆页
        response = redirect(reverse('users:login'))
        # 退出登陆时清除cookie中的username
        response.delete_cookie('username')

        return response


class UserInfoView(mixins.LoginRequiredMixin, View):
    '''用户中心'''

    def get(self, request):
        '''提供个人信息界面'''
        # if request.user.is_authenticated():
        return render(request, 'user_center_info.html')
        # else:
        #     return redirect(reverse('users:login'))


# TODO 提交一下到git仓库
