@echo off
chcp 65001 > nul
title PhotoToJewelry3D - Local Dev Server

echo ========================================================
echo   PhotoToJewelry3D & Anatomy Sculpt Studio
echo   ローカル開発サーバーを起動しています...
echo ========================================================
echo.

cd /d "%~dp0"

:: node_modulesの存在確認
if not exist "node_modules" (
    echo [INFO] 初回起動のため依存パッケージをインストールしています...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] npm install に失敗しました。Node.js がインストールされているか確認してください。
        pause
        exit /b %errorlevel%
    )
)

:: ブラウザでURLを自動オープン（2秒後）
start "" powershell -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:5173/'"

:: Vite 開発サーバー起動
echo [INFO] サーバーを起動します (URL: http://localhost:5173/)
echo [INFO] 終了するにはこのウィンドウを閉じるか Ctrl+C を押してください。
echo.

call npm run dev

pause
