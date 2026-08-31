import os
from typing import Any

from dotenv import set_key

from haima.engines.contract.settings import get_settings, ENV_FILE, reload_setting

ALLOWED_CONFIG_KEYS = [
    "DB_HOST", "DB_PORT", "DB_USER", "DB_NAME",
    "INSIGHT_ENGINE_API_KEY", "INSIGHT_ENGINE_BASE_URL", "INSIGHT_ENGINE_MODEL_NAME", "INSIGHT_ENGINE_MODEL_PROVIDER",
    "MEDIA_ENGINE_API_KEY", "MEDIA_ENGINE_BASE_URL", "MEDIA_ENGINE_MODEL_NAME", "MEDIA_ENGINE_MODEL_PROVIDER",
    "REPORT_ENGINE_API_KEY", "REPORT_ENGINE_BASE_URL", "REPORT_ENGINE_MODEL_NAME", "REPORT_ENGINE_MODEL_PROVIDER",
    "HOST_API_KEY", "HOST_BASE_URL", "HOST_MODEL_NAME", "HOST_MODEL_PROVIDER",
    "ANSPIRE_API_KEY", "ANSPIRE_BASE_URL"
]


def mark_secret(value:str)->str:
    if not value:
        return ''
    return f"****{value[-4:]}"


class SystemService:

    def get_config(self) -> dict[str, Any]:

        settings = get_settings()

        config_dict: dict[str, Any] = {}

        for key in ALLOWED_CONFIG_KEYS:
            value = getattr(settings,key,None)
            text = '' if value is None else value

            if key.endswith("_API_KEY"):
                text = mark_secret(value)
            config_dict[key] = text

        return config_dict


    def update_config(self,config_info:dict[str,Any]):

        # 1. 防御性校验
        unknow_keys = [key for key in config_info.keys() if key not in ALLOWED_CONFIG_KEYS]

        if unknow_keys:
            raise ValueError(f"未知的配置属性{'、'.join(unknow_keys)}")

        # 2.更新配置
        for key, value in config_info.items():
            set_key(ENV_FILE,key,value,quote_mode='never')
            # os.environ[key] = value   # 修改环境变量

        # 3.重新更新配置类
        reload_setting()


