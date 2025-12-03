@echo off
echo Installation du Systeme d'Irrigation Intelligent
echo ================================================
echo.

REM Mettre a jour pip
python -m pip install --upgrade pip

REM Installer les dependances
echo Installation des dependances...
pip install langchain langchain-openai langchain-community openai pandas numpy flask python-dotenv requests apscheduler werkzeug

echo.
echo Installation terminee!
echo.
echo N'oubliez pas de creer le fichier .env avec vos cles API.
echo.

pause




