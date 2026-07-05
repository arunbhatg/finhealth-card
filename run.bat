@echo off
set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
echo === FinHealth Card Setup ===
"%PY%" -m pip install -r requirements.txt
"%PY%" scripts/generate_data.py
"%PY%" scripts/train_model.py
echo.
echo === Starting app ===
"%PY%" -m streamlit run app/main.py