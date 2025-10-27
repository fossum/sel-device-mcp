@echo off
echo Starting FastAPI server for COM5 connection...
echo.
echo The server will be available at: http://localhost:8002
echo API documentation will be at: http://localhost:8002/docs
echo.
echo Press Ctrl+C to stop the server.
echo.

C:\development\ericfoss\sel-device-mcp\.venv\Scripts\uvicorn.exe src.server.main:app --host 127.0.0.1 --port 8000 --reload
