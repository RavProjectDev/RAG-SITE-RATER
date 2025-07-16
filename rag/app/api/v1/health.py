from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
def get_health(request: Request):
    return request.json()
