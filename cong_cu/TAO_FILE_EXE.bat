@echo off
setlocal
cd /d "%~dp0.."
echo Tao file EXE cho Windows. Buoc nay chi dung thu vien da cai dung requirements-build.txt, khong tu cai/ket noi mang.
echo Khong thay doi thu muc DU_LIEU.
echo Hay kich hoat moi truong rieng da cai requirements-build.txt truoc khi chay.
where python >nul 2>nul
if errorlevel 1 goto nopy
python -B cong_cu\DONG_GOI.py
if errorlevel 1 goto failed
echo Da tao SO_BAO_CAO_CA.exe ngay trong thu muc nay.
echo DB van nam o DU_LIEU ben canh EXE. Khong can chep DB vao ben trong EXE.
pause
exit /b 0
:nopy
echo Can Python trong moi truong rieng tren PATH de dong goi.
goto failed
:failed
echo Chua tao duoc EXE. Kiem tra thong bao loi o tren.
pause
exit /b 1
