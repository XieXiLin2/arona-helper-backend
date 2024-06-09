from fastapi.responses import JSONResponse


class AronaError(Exception):
    def __init__(self, message: str, status_code: int = 403):
        self.message = message
        self.status_code = status_code


def arona_error_handler(exc: AronaError):
    return JSONResponse(
        content={"status": exc.status_code, "msg": exc.message},
        status_code=exc.status_code,
    )
