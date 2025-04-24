from fastapi import APIRouter


# General Router for shared endpoints
general_router = APIRouter(prefix="/api", tags=["General"])


@general_router.get("/")
def read_root():
    return {"message": "Hello World"}
