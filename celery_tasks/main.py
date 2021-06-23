import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')
# 创建celery实例
app = Celery('celery_tasks')
# 加载队列配置文件
app.config_from_object('celery_tasks.config')
# 自动注册任务
app.autodiscover_tasks(['celery_tasks.sms'])
