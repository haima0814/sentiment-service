import uvicorn

from haima.engines.contract.settings import get_settings

if __name__ == '__main__':
    uvicorn.run(app='app.app:app',host=get_settings().HOST,port=get_settings().PORT)