@echo off
echo ============================================
echo  KuroAI Backend Startup Script
echo  Using Java 21 (Temurin, from VS Code ext)
echo ============================================
echo.

REM Use the working JDK 21 bundled with VS Code's Java extension
set JAVA_HOME=C:\Users\HP\.vscode\extensions\redhat.java-1.54.0-win32-x64\jre\21.0.10-win32-x86_64

echo [INFO] JAVA_HOME=%JAVA_HOME%
echo [INFO] Starting Spring Boot on http://localhost:8080 ...
echo [INFO] H2 Console available at http://localhost:8080/h2-console
echo [INFO]   JDBC URL : jdbc:h2:mem:kuroaidb
echo [INFO]   Username : sa  /  Password : password
echo [INFO] Press Ctrl+C to stop the server.
echo.

cd /d %~dp0
.\mvnw.cmd spring-boot:run
