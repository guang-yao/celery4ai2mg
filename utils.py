import time
from celery.result import AsyncResult
from . import celery_app, task_name_dict

    
def task_async(func_name,datas,priority=5):
    task = celery_app.send_task(task_name_dict[func_name]['task_name'], args=[datas,], kwargs={},priority=priority)
    soft_time_limit = task_name_dict[func_name].get('soft_time_limit', 120)
    if soft_time_limit is None: soft_time_limit = 120
    cost = 0
    while cost < soft_time_limit:
        task = AsyncResult(task.id)
        if task.state == 'SUCCESS':
            return task.result
        time.sleep(0.1)
        cost += 0.1
    return "celery async TimeOut!"