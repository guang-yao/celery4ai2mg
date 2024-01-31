from setuptools import setup

setup(
    name='celery_ai2mg',
    version='1.0.0',
    author='yaoguang',
    author_email='yaoguang@mgtv.com',
    description='快速构建celery异步任务',
    py_modules=['utils','tasks'],
    install_requires=[
        'celery==5.2.7',
        'celery-amqp-backend==1.0.0',
    ],
)