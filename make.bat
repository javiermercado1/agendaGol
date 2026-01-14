@echo off
set arg1=%1

if "%arg1%"=="init" (
    docker-compose up --build
) else if "%arg1%"=="start" (
    docker-compose up -d
) else if "%arg1%"=="stop" (
    docker-compose down
) else if "%arg1%"=="logs" (
    docker-compose logs -f
) else if "%arg1%"=="status" (
    docker-compose ps
) else if "%arg1%"=="clean" (
    docker-compose down -v
    del *.db 2>nul
    del auth_service\*.db 2>nul
    del roles_service\*.db 2>nul
    del fields_service\*.db 2>nul
    del reservations_service\*.db 2>nul
) else (
    echo Usage: make [init^|start^|stop^|logs^|status^|clean]
)
