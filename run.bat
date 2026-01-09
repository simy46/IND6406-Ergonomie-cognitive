@echo off
set PROJECT_ROOT=%~dp0
set PYTHONPATH=%PROJECT_ROOT%
py -3.12 "%PROJECT_ROOT%main_simulator.py"
pause
