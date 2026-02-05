@echo on
setlocal

:: Wechsle ins Script-Verzeichnis
cd /d "%~dp0"

python AnalyzePortfolio_Pipeline.py
endlocal
