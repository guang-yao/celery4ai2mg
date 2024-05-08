# result_persistent = False
# result_exchange = 'celery_result'
# result_exchange_type = 'direct'

worker_concurrency = 1  # 并发worker数

task_time_limit = 120 * 60  # 任务的硬时间限制，以秒为单位。如果这个时间限制被超过，处理任务的工作单元进程将会被杀死并使用一个新的替代。

task_soft_time_limit = 110 * 60

timezone = 'Asia/Shanghai'

CELERYD_FORCE_EXECV = True    # 非常重要,有些情况下可以防止死锁

worker_prefetch_multiplier = 1  # worker预取的任务数量

result_serializer = 'json'

worker_max_tasks_per_child = 5    # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露

worker_disable_rate_limits = True

task_acks_late = True

task_routes = {}

task_acks_on_failure_or_timeout = True

task_reject_on_worker_lost = False

task_track_started = True

task_queue_max_priority = 10

task_default_priority=5

broker_heartbeat = 86400

broker_heartbeat_checkrate = 10

"""
修改过期时间：
/root/miniconda3/lib/python3.8/site-packages/celery_amqp_backend/backend.py
line 62: func store_result:
在producer.publish内增加参数 
expiration=5,
"""
