import threading

def background_task():
    """喵～这是后台线程要运行的函数喵～"""
    print("后台任务开始运行喵～")
    thread = threading.Thread(target=main_background_task)
    thread.daemon = False  # 设置为守护线程，主线程结束时自动终止喵～
    thread.start()
    print("后台任务结束喵～")

def main_background_task :
    validate_config_files