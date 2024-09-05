from fastapi import FastAPI

from app.auth import auth_routes
from .routes import category_routes, article_routes

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "HELLO World"}


app.include_router(category_routes.router)
app.include_router(auth_routes.router)

app.include_router(article_routes.routers)
