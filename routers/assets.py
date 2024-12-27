from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_assets():
    return {"assets": ["Gold", "Silver", "Bitcoin", "Wheat", "Oil"]}


