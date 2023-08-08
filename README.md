# celery ai2mg


### 子项目构建

当需要将某个项目的函数托管到ai2mg的异步接口时，以下几步进行部署:
1. 新建git仓库，并将本项目，和目标项目的仓库放到新的git仓库下面
2. 构建目标函数，并在celery_ai2mg的config.ini中注册目标函数

下面分别详细说明
- git仓库
    新建仓库，获取到仓库地址`giturl`
    ```
    mkdir GIT_PATH && cd GIT_PATH
    git init
    git remote add origin [giturl]

    # 添加celery_ai2mg子仓库
    git submodule add https://git.imgo.tv/aiops/celery_ai2mg.git

    # 添加目标项目子仓库
    git submodule add https://git.imgo.tv/aiops/mangxiaozhi.git 

    # 提交改动
    git add . && git commit -m 'init'  && git push origin master
    ```
- 目标项目需包含可以执行的函数

- 配置config.ini文件
    1. 指定方法名，在接口调用时使用
    2. 添加方法的section, 格式请参考文件注释
    ps: 配置的参数，需满足from [importpath] import [func_name]

### 环境
1. celery环境
`pip install -r requeriments.txt`
2. 目标项目环境, 安装相应的环境
3. 构建docker

### celery运行

- 本项目的初始化，会将不同方法放在 名为 'ai2mg_' + func_name的队列中。(如chat_abs的func_name为`get_abs`，则其所在队列为`ai2mg_get_abs`)
- 运行时，需指定想要执行的队列名

单任务worker
```
export CELERY_MODE=dev && celery -A celery_ai2mg.tasks worker -Q ai2mg_get_abs -c 4 -l info -P prefork   # 测试环境
export CELERY_MODE=prod && celery -A celery_ai2mg.tasks worker -Q ai2mg_get_abs -c 4 -l info -P prefork  # 生产环境
```

多任务worker,不同队列以逗号分隔
```
export CELERY_MODE=dev && celery -A celery_ai2mg.tasks worker -Q ai2mg_get_abs,ai2mg_get_info -c 4 -l info -P prefork   # 测试环境
export CELERY_MODE=prod && celery -A celery_ai2mg.tasks worker -Q ai2mg_get_abs,ai2mg_get_info -c 4 -l info -P prefork  # 生产环境
```

### 任务调用
可以将celery_ai2mg放在内网触及的任何地方运行
```
from celery_ai2mg.utils import task_async
result = task_async(METHOD_NAME, FUNC_INPUT, priority=5)
print(result)
```

