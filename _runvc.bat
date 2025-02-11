@echo off
set ENV_NAME=env

rem 仮想環境が存在するか確認
if not exist %ENV_NAME% (
    echo 仮想環境 "%ENV_NAME%" を作成中...
    python -m venv %ENV_NAME%
    if errorlevel 1 (
        echo 仮想環境の作成に失敗しました。
        exit /b 1
    )
)

echo 仮想環境 "%ENV_NAME%" をアクティベートします...
call %ENV_NAME%\Scripts\activate
if errorlevel 1 (
    echo 仮想環境のアクティベートに失敗しました。
    exit /b 1
)

code .

