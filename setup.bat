@echo off
chcp 65001 >nul
echo ========================================
echo   SETUP VA KHOI DONG FLASK PROJECT
echo ========================================
echo.

REM Buoc 1: Cai dat virtualenv neu chua co
echo [1/6] Kiem tra va cai dat virtualenv...
python -m pip install --upgrade pip >nul 2>&1
python -m pip show virtualenv >nul 2>&1
if errorlevel 1 (
    echo    Dang cai dat virtualenv...
    python -m pip install virtualenv
    if errorlevel 1 (
        echo    LOI: Khong the cai dat virtualenv!
        pause
        exit /b 1
    )
    echo    Da cai dat virtualenv
) else (
    echo    virtualenv da duoc cai dat
)
echo.

REM Buoc 2: Tao moi truong ao neu chua ton tai
echo [2/6] Kiem tra moi truong ao...
if not exist "venv" (
    echo    Dang tao moi truong ao...
    python -m virtualenv venv
    if errorlevel 1 (
        echo    LOI: Khong the tao moi truong ao!
        pause
        exit /b 1
    )
    echo    Da tao moi truong ao
) else (
    echo    Moi truong ao da ton tai
)
echo.

REM Buoc 3: Kich hoat moi truong ao
echo [3/6] Kích hoạt môi trường ảo...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo    LOI: Khong the kich hoat moi truong ao!
    pause
    exit /b 1
)
echo    Da kich hoat moi truong ao
echo.

REM Bước 4: Cài đặt thư viện từ requirements.txt
echo [4/6] Cai dat thu vien tu requirements.txt...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo    LOI: Khong the cai dat thu vien!
        pause
        exit /b 1
    )
    echo    Da cai dat tat ca thu vien
) else (
    echo    CANH BAO: Khong tim thay file requirements.txt!
)
echo.

REM Buoc 5: Kiem tra va thiet lap file .env
echo [5/6] Kiểm tra cấu hình .env...
if not exist ".env" (
    if exist "env.example" (
        echo    File .env chua ton tai, dang tao tu env.example...
        copy env.example .env >nul
        echo    Da tao file .env tu env.example
        echo    Vui long chinh sua file .env voi thong tin thuc te!
    ) else (
        echo    CANH BAO: Khong tim thay file env.example!
        echo    Vui long tao file .env thuc cong voi cac bien moi truong can thiet.
    )
) else (
    echo    File .env da ton tai
)
echo.

REM Buoc 6: Khoi dong Flask
echo [6/6] Khoi dong Flask server...
echo.
echo ========================================
echo   DANG KHOI DONG FLASK...
echo ========================================
echo.

python src\main.py

pause

