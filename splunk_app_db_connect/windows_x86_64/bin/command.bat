@echo off
set JAVA_CMD=java.exe
IF EXIST %~dp0/customized.java.path (
    set /p JAVA_CMD=<"%~dp0/customized.java.path"
    goto exec
)

IF EXIST %JAVA_HOME% (
    set JAVA_CMD=%JAVA_HOME%\bin\java.exe
    goto exec
)

:exec
"%JAVA_CMD%" %*
