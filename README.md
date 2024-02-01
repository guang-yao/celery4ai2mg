# 快速部署celery ai2mg

### 安装
pip install git+https://git.imgo.tv/aiops/celery_ai2mg.git@package

### 使用

**需创建一个新的文件**，比如main或api文件，用来创建任务

- 使用
    ```
    from celery4ai2mg import ctoperate  #  导入模块
    ctoperate.update_broker_backend(  #  初始化连接串
        broker_url="amqp://ai2mg:as78113hasf1v@10.200.16.242/ai2mg-prod",  
        backend_url="celery_amqp_backend.AMQPBackend://ai2mg:as78113hasf1v@10.200.16.242/ai2mg-prod"
        # broker_url = "sentinel://10.43.208.66:7850;sentinel://10.43.208.64:7495;sentinel://10.43.208.65:7493;",
        # backend_url = "sentinel://10.43.208.66:7850;sentinel://10.43.208.64:7495;sentinel://10.43.208.65:7493;",
        # broker_transport_options = {"master_name":"ad-effect_platform-aliyun-new2-6450"}
    )

    from fuinc import func_test2  # 导入需要异步的函数
    func_name1 = ctoperate.create_celery_task(func_test2, soft_time_limit=10, bind=False)  # 创建任务
    ctoperate.done()  # 任务定义完成

    # 直接调用
    # task = ctoperate.task_async(func_test2, args=[], kwargs={}, priority=5)
    task = ctoperate.task_async(func_name=func_name1, args=[], kwargs={}, priority=5)
    if task is not None:
        print(task.id)
        for _ in range(4):
            task = ctoperate.async_result(task.id)
            print(task.state)
            print(task.result)
            time.sleep(1)

    # ... 其他业务代码，比如api
    ```

### celery运行
运行的参数内包含--run_celery选项时，执行ctoperate.done()之前的代码后，退出程序并执行celery命令
--run_celery 后面的参数为celery的其他函数，会补充到命令行的后面。
```
python main.py --run_celery  -c 1 -l info -P prefork
```
### 调用
运行的参数内不包含--run_celery选项时，会直接执行业务代码，不会启动celery。如:
```
python main.py
```
