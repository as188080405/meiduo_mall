import re

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User


# 判断使用用户名/手机号登录
def get_user_by_account(account):
    try:
        if not (re.match(r'^1[3-9]\d{9}$', account)):
            user = User.objects.get(username=account)
        else:
            user = User.objects.get(mobile=account)
    except user.DoesNotExist:
        return None
    else:
        return user


# 自定义用户认证（手机号或密码登录）
class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user
