"""
task -> research + async
research = create_task + {task_id:research_info} + return
get = research(task_id)
submit = asyncio.create_task()  -> async_task.add  ->add_done_callback

"""

"""
启动研究的异步任务,建立相关协程对象

"""


list2 = [{"a": 8}, {'b': 5},{'x':48}]
s = sorted(list2,key=lambda x:list(x.values())[0],reverse=True)
print(s)
