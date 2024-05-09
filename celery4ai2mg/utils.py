import time
import json
import os, re
import inspect
import configparser
from celery.result import AsyncResult

import copy

class CelertTaskOperate:
    def __init__(self, celery_app, config_operate, task_name_dict,just_create_task=True,is_celery_cmd=False) -> None:
        self.celery_app = celery_app
        self.config_operate = config_operate
        self.task_name_dict = task_name_dict
        self.just_create_task = just_create_task
        self.is_celery_cmd = is_celery_cmd
    
    def update_queue(self, queue):
        print(f"update queue: {queue}")
        """
        {
        'mmapp_pointcube.*': {'queue': 'mmapp_pointcube'},
        'mmapp_schedule.*': {'queue': 'mmapp_schedule'},
        }
        """
        queue_dict =  {
            f"{queue}.*": {'queue': queue}
        }
        self.celery_app.conf.task_routes.update(queue_dict)
    
    def add_celery_config(self, key, value):
        if isinstance(value,  str):
            value_ = value.strip('"').strip("'")
        elif isinstance(value, list) or isinstance(value, dict):
            value_ = copy.deepcopy(value)
            value = json.dumps(value)
        setattr(self.celery_app.conf, key, value_)
        self.config_operate.save_task_config("celery", key, value)
        
    def update_broker_backend(self, broker_url,  backend_url, broker_transport_options = None):
        """
            保存连接串信息
            broker_url = "sentinel://10.43.208.66:7850;sentinel://10.43.208.64:7495;sentinel://10.43.208.65:7493;"
            backend_url = "sentinel://10.43.208.66:7850;sentinel://10.43.208.64:7495;sentinel://10.43.208.65:7493;"
            broker_transport_options = {"master_name":"ad-effect_platform-aliyun-new2-6450"}
            celery_amqp_backend.AMQPBackend://ai2mg:as78113hasf1v@10.200.16.242/ai2mg-prod
        """
        self.add_celery_config('broker_url', broker_url)
        
        # 如果backend_url为amqp开头的连接串，需将其改为celery_amqp_backend
        if backend_url.startswith('amqp://'):
            backend_url = re.sub(r"^amqp://", "celery_amqp_backend.AMQPBackend://", backend_url)
        self.add_celery_config('backend_url', backend_url)
        
        if broker_transport_options is not None:
            self.add_celery_config('broker_transport_options', broker_transport_options)
    
    def create_celery_task(self, func_or_class, task_name="",queue="", soft_time_limit=60*60, bind=False,classbase=False, create_task=True):
        func_name = func_or_class.__name__
        task_name = f"task_{func_name}" if task_name  == "" else task_name
        queue = f"aimg_{func_name}" if queue  == "" else queue
        task_full_name = f"{queue}.{func_name}"
        
        self.config_operate.update_func(func_or_class, task_name, queue, soft_time_limit=soft_time_limit, bind=bind,classbase=classbase)
        self.update_queue(queue)
        
        if not create_task:
            return task_name
        print("create_task ...")
        if classbase:
            @self.celery_app.task(bind=True, base=func_or_class,name=task_name, soft_time_limit=soft_time_limit,max_retries=3)
            def celery_task(self, *args, **kwargs):
                return self.run_process(*args, **kwargs)
        elif bind:
            @self.celery_app.task(bind=True, name=task_full_name, soft_time_limit=soft_time_limit)
            def celery_task(self, *args, **kwargs):
                return func_or_class(self, *args, **kwargs)
        else:
            @self.celery_app.task(bind=False, name=task_full_name, soft_time_limit=soft_time_limit)
            def celery_task(*args, **kwargs):
                return func_or_class(*args, **kwargs)
            
        self.task_name_dict[task_name] = {"task_name":task_full_name,"soft_time_limit":soft_time_limit}
        return task_name
    
    def task_async(self, func=None,func_name="", args=[],kwargs={} ,priority=5):
        if self.just_create_task: return
        if func_name == "" and func is None:
            raise "请输入函数，或者函数名"
        func_name = func.__name__ if func_name == "" else func_name
        if func_name in self.task_name_dict:
            task_name = self.task_name_dict[func_name]['task_name']
        elif f"task_{func_name}" in self.task_name_dict:
            task_name = self.task_name_dict[f"task_{func_name}"]['task_name']
        else:
            raise "错误的函数名"
        return self.celery_app.send_task(task_name, args=args, kwargs=kwargs,priority=priority)

    def async_result(self, taskid):
        if self.just_create_task: return
        return AsyncResult(taskid)
    
    def done(self):
        if self.just_create_task:
            if self.is_celery_cmd:
                print(f"ctoperate.done() 不能和执行的函数放在同一个文件中，否则会执行不成功！！！")
                print(f"清理.celery文件夹")
                os.system(f"rm -r {self.config_operate.local_config_path}")
            exit(0)

class ConfigOperate:
    def __init__(self, base_dir) -> None:
        self.base_dir = base_dir
        tmp_dir = os.path.join(self.base_dir, ".celery")
        os.makedirs(tmp_dir, exist_ok=True)
        self.local_config_path = os.path.join(tmp_dir, "config.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.local_config_path)
        if not os.path.exists(self.local_config_path):
            self.save()
    
    def update_func(self, function, fname, queue, soft_time_limit=None, bind=False,classbase=False):
        file_path = inspect.getfile(function)
        relpath =  os.path.relpath(file_path, self.base_dir)
        assert relpath.endswith(".py")
        importpath = '.'.join(relpath[:-3].split('/'))
        func_name = function.__name__
        
        if 'tasks' in self.config:
            name_list = self.config.get('tasks', 'name_list').strip().split(',')
            name_list = [i for i in name_list if i != ""] + [fname]
            name_list = list(set(name_list))
        else:
            self.config.add_section('tasks')
            name_list = [fname]
        self.config.set('tasks', 'name_list', ','.join(name_list))
        
        if fname not in self.config:
            self.config.add_section(fname)
    
        self.config.set(fname, 'importpath', importpath)
        self.config.set(fname, 'func_name', func_name)
        self.config.set(fname, 'bind', str(bind))
        self.config.set(fname, 'classbase', str(classbase))
        self.config.set(fname, 'queue', queue)
        if soft_time_limit is not None:
            self.config.set(fname, 'soft_time_limit', str(soft_time_limit))
        self.save()

    def save_task_config(self, selection, key, value):
        if selection not in self.config:
            self.config.add_section(selection)
        self.config.set(selection, key, value)
        self.save()
    
    def save(self):
        # 写入 INI 文件
        with open(self.local_config_path, 'w') as configfile:
            self.config.write(configfile)
        
    def lastest_config(self):
        config = configparser.ConfigParser()
        config.read(self.local_config_path)
        return config
    
def health():
    print(f"package health")