import uvicorn
from arona_helper_backend.config import config

# region runner
if __name__ == "__main__":
    uvicorn.run(
        app="arona_helper_backend:app",
        host=config.fastapi.host,
        port=config.fastapi.port,
        log_level=config.fastapi.log_level,
        reload=config.fastapi.reload,
    )
# endregion
