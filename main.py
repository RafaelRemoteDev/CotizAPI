import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from api.endpoints import router as alerts_router
from api.endpoints import router as assets_router
from api.endpoints import router as daily_router
from api.endpoints import router as start_router
from api.endpoints import router as weekly_router
from bot.config_bot import main as bot_main
from managers.assets_manager import actualizar_todos_los_precios

# Cargar variables de entorno
load_dotenv()

app = FastAPI()


@app.get("/")
def read_root():
    return {"¡CotizAPI está funcionando correctamente! 🤖💸🐂"}


app.include_router(start_router, prefix="")
app.include_router(assets_router, prefix="")
app.include_router(daily_router, prefix="")
app.include_router(weekly_router, prefix="")
app.include_router(alerts_router, prefix="")

if __name__ == "__main__":
    print("⏳ Inicializando y actualizando precios de los activos en la base de datos...")
    actualizar_todos_los_precios()
    print("✅ Precios iniciales actualizados.")
    bot_main()
    uvicorn.run("main:app", host="127.0.0.1", port=8032)
