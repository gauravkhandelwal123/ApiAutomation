@echo off
rem scheduler_setup.bat – registers a Windows scheduled task to run the API test framework every 4 days at 02:00

set TASK_NAME=APITestFrameworkReport
set SCRIPT_PATH=%~dp0api_test_framework\runner.py
set PYTHON_EXE=python
rem Adjust frequency: using "/SC DAILY" with /MO 4 for every 4 days
schtasks /Create /F \
    /TN "%TASK_NAME%" \
    /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" \
    /SC DAILY /MO 4 /ST 02:00

echo Scheduled task "%TASK_NAME%" created to run every 4 days at 02:00.
pause
