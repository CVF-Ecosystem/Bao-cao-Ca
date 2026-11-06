@echo off
setlocal
cd /d "%~dp0"
set FAIL=0

where py >nul 2>nul
if not errorlevel 1 (
  set PYTHON=py -3
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set PYTHON=python
  ) else (
    echo Can Python 3.9 tro len de kiem thu.
    set FAIL=1
    goto done
  )
)

echo === Kiem thu Python ===
%PYTHON% -m unittest discover -p "KIEM_THU*.py" -v
if errorlevel 1 set FAIL=1

echo.
echo === Kiem thu giao dien JavaScript ===
where node >nul 2>nul
if errorlevel 1 (
  echo CANH BAO: may chua cai Node.js nen BO QUA cac bo KIEM_THU*.js.
  echo Giao dien chua duoc kiem thu tren may nay.
  set FAIL=1
) else (
  for %%f in (KIEM_THU*.js) do (
    node "%%f"
    if errorlevel 1 (
      echo THAT BAI: %%f
      set FAIL=1
    )
  )
)

:done
echo.
if "%FAIL%"=="0" (echo TAT CA KIEM THU DEU QUA.) else (echo CO KIEM THU THAT BAI HOAC BI BO QUA. Xem thong bao o tren.)
pause
endlocal & exit /b %FAIL%
