# Endpoints de variaciones

from fastapi import APIRouter

router = APIRouter()

@router.get("/daily")
def get_daily_variations():
    return {"message": "Daily variations not implemented yet"}

@router.get("/weekly")
def get_weekly_variations():
    return {"message": "Weekly variations not implemented yet"}