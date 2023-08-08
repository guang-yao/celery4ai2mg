#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@file: tasks.py
@time: 2021/11/9
@author: yaoguang
@contact: yaoguang@mgtv.tv
'''
from __future__ import print_function
from __future__ import division
from ctasks import task_queue,task_config_list,is_celery
from ctasks import celery_app
import importlib

def gen_celery_task(task_config):
    """
    动态创建celery task.
    filename: 文件的相对位置，用于导入
    classname: 任务类的名称，用于导入
    method_name: 任务的方法名，需与任务__init__中的method_name相同
    queue: 任务的队列名称, 为空时代表默认队列
    time_limit: 任务的时间限制，不填则为config里的默认数字
    """
    func_name = task_config['func_name']
    queue = task_config['queue']
    importpath = task_config['importpath']
    soft_time_limit = task_config.get('soft_time_limit', None)
    
    print(f"init func_name: {func_name} from {importpath}")
    script = importlib.import_module(importpath)
    task_name = f'{queue}.{func_name}' if len(queue) > 0 else func_name
    @celery_app.task(bind=True, name=task_name, soft_time_limit=(soft_time_limit))
    def celery_task(self, *args, **kwargs):
        return getattr(script, func_name)(*args, **kwargs)


task_queues = task_queue.split(',')
to_realize_task = [i for i in task_config_list if i['queue'] in task_queues]
print(to_realize_task)
if not is_celery: 
    print(f"python scripts, pass create celery task")
else:
    for task_config in to_realize_task:
        gen_celery_task(task_config)
