import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app.routers.analyze import router as analyze_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(title="Indian Market Risk Intelligence", version="1.0.0")

# Setup templates and optionally static mounts
templates = Jinja2Templates(directory="app/templates")

app.include_router(analyze_router)

@app.get("/")
async def root_dashboard(request: Request):
    """Serves the main frontend UI."""
    return templates.TemplateResponse(
        request=request, name="index.html", context={"request": request}
    )
