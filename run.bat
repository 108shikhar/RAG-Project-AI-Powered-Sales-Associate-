@echo off
title Shopsy AI Sales Associate - Server Launcher
color 0A
echo ============================================================
echo   SHOPSY AI SALES ASSOCIATE (Shopsy Mitr)
echo   Sequential Agentic RAG with Groq LPU + all-mpnet-base-v2
echo ============================================================
echo.
echo Starting web server on http://localhost:8000 ...
python run_server.py
pause
