from django.conf.urls import url
from . import views


urlpatterns = [
    # 注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # 用户名是否重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.RegisterView.as_view()),
    # 手机号是否重复
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.MobileCountView.as_view()),

    # TODO login 和 logout 的路由

    # 用户中心
    url(r'^info', views.UserInfoView)
]