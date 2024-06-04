import time
import celery
from fuinc import func_test2
        
from celery4ai2mg import ctoperate

ctoperate.update_broker_backend(
    broker_url="amqp://ai2mg:as78113hasf1v@10.200.16.242/ai2mg-prod",  
    backend_url="celery_amqp_backend.AMQPBackend://ai2mg:as78113hasf1v@10.200.16.242/ai2mg-prod", 
    # broker_url = "sentinel://10.43.208.66:7850;sentinel://10.43.208.64:7495;sentinel://10.43.208.65:7493;",
    # backend_url = "sentinel://10.43.208.66:7850;sentinel://10.43.208.64:7495;sentinel://10.43.208.65:7493;",
    # broker_transport_options = {"master_name":"ad-effect_platform-aliyun-new2-6450"}
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
