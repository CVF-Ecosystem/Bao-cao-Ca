@echo off
setlocal
cd /d "%~dp0.."
echo Tao file EXE cho Windows. Buoc nay can Internet de cai PyInstaller neu chua co.
echo Khong thay doi thu muc DU_LIEU.
where py >nul 2>nul
if errorlevel 1 goto nopy
py -3 -m pip install pyinstaller
if errorlevel 1 goto failed
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name SO_BAO_CAO_CA --add-data "giao_dien.html:." --add-data "tai_nguyen:tai_nguyen" --add-data "DANH_MUC_MAU:DANH_MUC_MAU" --add-data "MAU_BAO_CAO.xlsx:." MO_BAO_CAO_CA.pyw
if errorlevel 1 goto failed
copy /Y "dist\SO_BAO_CAO_CA.exe" "SO_BAO_CAO_CA.exe"
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
