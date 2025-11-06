#!/usr/bin/env python3
"""
Запускной скрипт для Campus Manager
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Устанавливаем рабочую директорию
os.chdir(project_root)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5500, reload=True)