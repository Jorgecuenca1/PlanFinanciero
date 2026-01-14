@echo off
echo ========================================
echo   Sistema de Habilitacion de Servicios
echo   Resolucion 3100 de 2019
echo ========================================
echo.
echo Iniciando servidor Django...
echo.
echo Acceder a: http://127.0.0.1:8020
echo Admin: http://127.0.0.1:8020/admin
echo.
echo Usuario: admin@habilitacion.com
echo Password: admin123
echo.
echo Presione Ctrl+C para detener el servidor
echo ========================================
echo.
python manage.py runserver 8020
pause
