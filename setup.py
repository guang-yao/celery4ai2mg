from setuptools import setup, find_packages

setup(
    name="celery4ai2mg",
    version="0.0.1",
    keywords=("celery", "mgtv"),
    description="快速构建celery异步任务",
    long_description="long_description",
    license="MIT Licence",

    url="https://git.imgo.tv/aiops/celery_ai2mg.git@package",
    author="yaoguang",
    author_email="yaoguang@mgtv.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        'celery==5.2.7',
        'celery-amqp-backend==1.0.0',
        'redis==5.0.1',
        'amqp==5.1.1'
        ],
    package_data={
        'celery4ai2mg': ['config.ini'],
    }
)