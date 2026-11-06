@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 BAO_CAO_CA.py
  goto done
)
where python >nul 2>nul
if not errorlevel 1 (
  python BAO_CAO_CA.py
  goto done
)
echo May chua co Python 3.9 tro len.
echo Can cai Python roi mo lai file nay. Tool khong can cai them thu vien.
:done
if errorlevel 1 pause
endlocal
