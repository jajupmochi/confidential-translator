import sys
import os
from pathlib import Path

# Add the current directory to sys.path to resolve 'app' module
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import export, health, history, models, translate, ollama, settings as settings_router, streaming, glossary
from app.core.config import settings
from app.core.database import init_db

# Check for --debug argument and override settings immediately before logger init
if "--debug" in sys.argv:
    settings.debug = True

print("Starting Confidential Translator...")
logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger("app.main")
logger.info("Initializing application...")

if settings.debug:
    logger.debug("🛠️ Debug mode is enabled. Developer logs will be printed.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Confidential Translator backend is ready.")
    yield
    logger.info("Shutting down...")
    from app.services.ollama_service import ollama_service
    await ollama_service.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A fully offline, privacy-first document translation system powered by local LLMs. "
        "Supports text, PDF, images (OCR), XLSX, CSV, Markdown, and DOCX translation "
        "across Chinese, English, German, and French."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for local standalone use
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health.router, prefix="/api")
app.include_router(translate.router, prefix="/api")
app.include_router(streaming.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(ollama.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(glossary.router, prefix="/api")

# Serve Vue frontend static files
# Detect if running in a PyInstaller bundle
if hasattr(sys, "_MEIPASS"):
    # When packaged, static files are usually in app/static relative to _MEIPASS
    # based on the --add-data "app/static:app/static" flag
    static_dir = Path(sys._MEIPASS) / "app" / "static"
else:
    # When running from source
    static_dir = Path(__file__).parent / "static"

logger.info(f"Looking for static assets in: {static_dir}")

if static_dir.exists():
    # Mount static files at root. 'html=True' handles index.html for root path
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
else:
    logger.warning(f"Static directory not found at {static_dir}. GUI will not be served.")
    
    @app.get("/")
    async def root():
        """Fallback root when static files are missing."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "message": "Static files missing. If you are developing, build the frontend first.",
            "static_path_tried": str(static_dir),
            "docs": "/docs",
        }


if __name__ == "__main__":
    import threading
    import time
    import uvicorn
    import webbrowser
    import subprocess
    import socket

    def is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    def is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    def open_browser():
        """Wait for the server to spin up, then open UI in the default browser."""
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:8000/")

    def kill_old_instances(port: int):
        """Automatically kill previous instances of the app if they occupy the port."""
        try:
            import psutil
        except ImportError:
            logger.warning("psutil not found, skipping port conflict resolution.")
            return False
        
        import os
        current_pid = os.getpid()
        cleared = False
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Only check processes that actually have connections to avoid overhead
                connections = proc.net_connections(kind='inet')
                for conn in connections:
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        # Found a process on the port. Check if it's us.
                        if proc.info['pid'] == current_pid:
                            continue
                        
                        # Identify if it's a previous translator instance
                        cmdline = " ".join(proc.info['cmdline'] or [])
                        # Check for binary name or module run
                        if "confidential-translator" in cmdline or "app.main" in cmdline or "uvicorn" in cmdline:
                            logger.info(f"Killing previous instance (PID: {proc.info['pid']}) on port {port}...")
                            proc.terminate()
                            try:
                                proc.wait(timeout=3)
                            except psutil.TimeoutExpired:
                                proc.kill()
                            cleared = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return cleared


    # Ensure port is clear before starting
    kill_old_instances(8000)
    
    logger.info("Starting standalone Confidential Translator...")
    from app.services.ollama_service import ollama_service
    ollama_service.start_server()
    threading.Thread(target=open_browser, daemon=True).start()
    
    log_level = "debug" if settings.debug else "info"
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level=log_level)
