import time
import celery
from fuinc import func_test2
        
from celery4ai2mg import ctoperate

ctoperate.update_broker_backend(
    broker_url="",  
    backend_url=""
)
class STask(celery.Task):
    def __init__(self):
        print(f"init STask")
    
    def run_process(self):
        print(f"process")

# func_name1 = ctoperate.create_celery_task(STask, soft_time_limit=10, classbase=True)  
func_name1 = ctoperate.create_celery_task(func_test2, soft_time_limit=10, bind=False)
ctoperate.done()


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
