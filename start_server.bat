@echo off
set PORT=8000
echo Starting FastAPI server for COM5 connection...
echo.
echo The server will be available at: http://localhost:%PORT%
echo API documentation will be at: http://localhost:%PORT%/docs
echo.
echo Press Ctrl+C to stop the server.
echo.

python -m uvicorn src.server.main:app --host 127.0.0.1 --port %PORT% --reload
