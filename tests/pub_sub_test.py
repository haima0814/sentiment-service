import datetime
from collections.abc import Callable
from typing import Any

container:dict[str,list] = {}


# 订阅者
def subscribe(event_type:str,call_back:Callable):
    """
    :param event_type: 事件类型
    :param call_back: 函数对象
    :return:
    """
    if event_type not in container:
        container[event_type] = []

    container[event_type].append(call_back)


# 发布者
def publish(event_type:str,event_data:dict[str,Any]):
    if event_type in container:
        for callback in container[event_type]:
            callback(event_data)



def tom_subscribe_weather(event_data:dict[str,Any]):
    print(f"tom收到了天气事件类型的数据:{event_data}")

def jack_subscribe_ai(event_data: dict[str, Any]):
    print(f"jack收到了AI事件类型的数据:{event_data}")



subscribe("weather",tom_subscribe_weather)
subscribe("ai",tom_subscribe_weather)
subscribe("ai", jack_subscribe_ai)


publish('weather',{"text":"你好天气之子"})
publish("ai",{"new": "gpt6发布了", "time": datetime.datetime.now()})