from django.conf.urls import url

from apps.contents import views

urlpatterns = [
    url(r'^index/$', views.IndexView.as_view(), name='index'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_]{5,20})/count/$', views.UsernameCountView.as_view(), name='usernameCount'),
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view(), name='mobileCount'),
]
