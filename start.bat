@echo off
chcp 65001 >nul
echo ========================================
echo   PuzzleStore - Запуск проекта
echo ========================================
echo.

echo [1/4] Запуск PostgreSQL в Docker...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось запустить Docker. Убедись, что Docker Desktop запущен.
    pause
    exit /b 1
)

echo.
echo [2/4] Ожидание готовности PostgreSQL...
timeout /t 5 /nobreak >nul

echo [3/4] Активация виртуального окружения...
call .venv\Scripts\activate.bat

echo [4/4] Запуск Django сервера...
echo.
echo ========================================
echo   Сервер запущен: http://127.0.0.1:8000/
echo   Админка:        http://127.0.0.1:8000/admin/
echo ========================================
echo.

python manage.py runserver

echo.
echo Остановка PostgreSQL...
docker-compose stop
pause