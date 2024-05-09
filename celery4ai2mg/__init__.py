#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@file: __init__.py
@time: 2021/11/23
@author: yaoguang
@contact: yaoguang@mgtv.tv
'''

"""
任务列表配置
filename: 文件的相对位置，用于导入
classname: 任务类的名称，用于导入
method_name: 任务的方法名，需与任务__init__中的method_name相同
queue: 任务的队列名称
time_limit: 任务的时间限制，不填则为config里的默认数字
schedule: 定时任务时间间隔
"""
import os, sys, json
import argparse
import configparser
import celery, kombu, amqp
from kombu import Queue, Exchange
from celery import Celery
from celery.concurrency import asynpool

from .utils import ConfigOperate,CelertTaskOperate
BASE_DIR = os.getcwd()
print(f"celery_app BASE_DIR: {BASE_DIR}")
sys.path.append(BASE_DIR)

# -------------------获取环境变量参数------------------
print(f"package version: \n   celery: {celery.__version__}, \n   kombu: {kombu.__version__}, \n   amqp: {amqp.__version__}")
version = os.getenv('CELERY_MODE','dev')
print(f"CELERY_MODE: {version}")

config_operate = ConfigOperate(BASE_DIR)
# -------------------获取环境变量参数------------------

# 获取当前队列参数与运行参数
parser = argparse.ArgumentParser()
parser.add_argument('-Q',type=str, default='')  # --queue
parser.add_argument("--run_celery", action="store_true", help="Enable verbose mode")

args, unknown = parser.parse_known_args()
print(f"task_queue: {args.Q}")
task_queue = args.Q
is_celery_cmd = 'celery' == os.path.basename(sys.argv[0])
run_celery = args.run_celery
just_create_task = run_celery or not is_celery_cmd
print(f"args.run_celery: {run_celery}")
print(f"is_celery_cmd: {is_celery_cmd}")
print(f"just_create_task: {just_create_task}")

if run_celery:
  from .atexit_run import quit_uvicorn
  
# 通用celery配置
asynpool.PROC_ALIVE_TIMEOUT = 3600.0
celery_app = Celery('tasks')

celery_app.config_from_object(f"celery4ai2mg.config")
celery_app.conf.worker_proc_alive_timeout = 3600

# 提取任务配置
task_config_list,task_name_dict = [], {}
config = config_operate.lastest_config()
if 'tasks'  in config:
  methodnames = config['tasks']['name_list'].strip().split(',')
  methodnames  = [i for i in  methodnames if i!=""]
  for method_name in methodnames:
    importpath = config[method_name].get('importpath', None)
    if importpath is None:
      print(f"Error! cannot find importpath with method_name {method_name}")
      continue
    
    soft_time_limit = config[method_name].get('soft_time_limit', None)
    func_name = config[method_name].get('func_name', method_name)
    queue = config[method_name].get('queue', f"ai2mg_{func_name}")
    if soft_time_limit is not None:
      soft_time_limit = int(soft_time_limit)
    class_name = config[method_name].get('class_name', None)
    bind = config[method_name].get('bind', "False")
    task_config_list.append({
      "importpath":importpath,
      "func_name":func_name,
      "queue":queue,
      'soft_time_limit':soft_time_limit,
      "class_name":class_name,
      "bind":str(bind)
      })
    task_name = f'{queue}.{func_name}' if len(queue) > 0 else func_name
    task_name_dict[method_name] = {"task_name":task_name,"soft_time_limit":soft_time_limit}

if 'celery' in config:
  celery_app.conf.broker_url = config[f'celery']["broker_url"].strip('"').strip("'")
  celery_app.conf.result_backend = config[f'celery']["backend_url"].strip('"').strip("'")
  celery_app.conf.celery_queues = (
    Queue('default', Exchange('default'), routing_key='default', queue_arguments={'x-max-priority': 10}),
  )
  broker_transport_options = config[f'celery'].get("broker_transport_options", None)
  if broker_transport_options is not None:
    broker_transport_options = json.loads(broker_transport_options)
    celery_app.conf.broker_transport_options = broker_transport_options
    celery_app.conf.result_backend_transport_options = broker_transport_options

"""
队列信息
key: 任务名称，*通配符代表所有。 value: 队列信息
{
    'mmapp_pointcube.*': {'queue': 'mmapp_pointcube'},
    'mmapp_schedule.*': {'queue': 'mmapp_schedule'},
    }
"""
queue_list = list(set([i['queue'] for i in task_config_list]))
queue_dict = {f"{c_queue}.*": {'queue':c_queue} for c_queue in queue_list if len(c_queue) > 0}

celery_app.conf.task_routes.update(queue_dict)
ctoperate = CelertTaskOperate(
  celery_app=celery_app, 
  config_operate=config_operate, 
  task_name_dict=task_name_dict, 
  just_create_task=just_create_task,
  is_celery_cmd=is_celery_cmd
  )