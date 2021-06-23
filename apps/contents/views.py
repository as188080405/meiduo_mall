from asyncio.log import logger

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.users.models import User


class IndexView(View):
    """ 获取首页 """
    def get(self, request):
        return render(request, 'index.html')

class UsernameCountView(View):
    """ 验证用户名是否重复 """
    def get(self, request, username):
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return http.HttpResponse({'code': 400, 'errmsg': '数据库异常'})
        return http.JsonResponse({'code': 0, 'count': count})

class MobileCountView(View):
    def get(self, request, mobile):
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            logger.error(e)
            return http.HttpResponse({'code': 400, 'errmsg': '数据库异常'})
        return http.JsonResponse({'code': 0, 'count': count})
