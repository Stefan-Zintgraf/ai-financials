@echo on
setlocal
cd /d "%~dp0Scripts"
python AnalyzeIbkrPortfolio.py
echo.
pause
endlocal
