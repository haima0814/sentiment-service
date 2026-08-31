from fastapi import APIRouter

from haima.app.dependecies import SystemServiceDep
from haima.app.schemas.system_schema import ConfigResponse, ConfigUpdateRequest

router = APIRouter(prefix='/api/config',tags=['系统配置信息路由'])

@router.get(path='',response_model=ConfigResponse)
def get_config_endpoint(service:SystemServiceDep):
    config_info = service.get_config()
    return ConfigResponse(config=config_info)


@router.post(path='')
def update_config_endpoint(request:ConfigUpdateRequest,
                           service:SystemServiceDep):
    service.update_config(request.root)