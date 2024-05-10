import atexit
import signal
import sys
import os

os.environ['quit_signal'] = '0'
run_command_key_word = "--run_celery"


@atexit.register
def quit_uvicorn():
    """勾子函数，在主程序运行结束时判断是否需要执行celery, 自动获取主程序中注册的队列，并运行"""
    quit_signal = os.getenv("quit_signal", '0')
    if int(quit_signal) > 0: 
        return
    os.environ['quit_signal'] = str(int(quit_signal)  + 1)
    if run_command_key_word in sys.argv:
        from . import celery_app
        print(sys.argv)
        print(celery_app.conf.task_routes)
        queues = ','.join([i.strip(".*") for i in celery_app.conf.task_routes])
        
        extra_args = ' '.join(sys.argv[sys.argv.index(run_command_key_word) + 1:])
        cmd = f"celery -A celery4ai2mg.tasks worker -Q {queues} {extra_args}"
        CUDA_VISIBLE_DEVICES = os.environ.get('CUDA_VISIBLE_DEVICES', None)
        if CUDA_VISIBLE_DEVICES is not None:
            cmd = f"CUDA_VISIBLE_DEVICES={CUDA_VISIBLE_DEVICES} {cmd}"
        print(cmd)
        os.system(cmd)
