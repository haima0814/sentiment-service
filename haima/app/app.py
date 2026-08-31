from fastapi import FastAPI

from haima.app.exceptions.exception_handlers import register_exception_handlers
from haima.app.routers.rest import system_router

app = FastAPI(description='掌握一切')

register_exception_handlers(app)

app.include_router(system_router.router)