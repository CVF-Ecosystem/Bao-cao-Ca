@echo off
setlocal
cd /d "%~dp0.."
echo Tao file EXE cho Windows. Buoc nay can Internet de cai PyInstaller neu chua co.
echo Khong thay doi thu muc DU_LIEU.
where py >nul 2>nul
if errorlevel 1 goto nopy
py -3 cong_cu\DONG_GOI.py
if errorlevel 1 goto failed
echo Da tao SO_BAO_CAO_CA.exe ngay trong thu muc nay.
echo DB van nam o DU_LIEU ben canh EXE. Khong can chep DB vao ben trong EXE.
pause
exit /b 0
:nopy
echo Can Python co lenh py tren may Windows de dong goi.
goto failed
:failed
echo Chua tao duoc EXE. Kiem tra thong bao loi o tren.
pause
exit /b 1
