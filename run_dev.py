import sys
from pathlib import Path
from dotenv import load_dotenv
import os
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "app"

# Добавляем backend в sys.path, чтобы импортировался main/app.*
sys.path.insert(0, str(BACKEND_DIR))

# Подхватываем dev-окружение (override, чтобы перебить системные ENV)
load_dotenv(BASE_DIR / ".env", override=True)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        env_file=str(BASE_DIR / ".env"),
        reload=True,
    )
