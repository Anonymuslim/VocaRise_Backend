@echo off
title Lancement de VocaRise
color 0A

echo.
echo ----------------------------------------
echo      🚀 Lancement de l'application
echo ----------------------------------------

REM ✅ Étape 1 : Créer l'environnement virtuel s’il n'existe pas
IF NOT EXIST "venv\" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
)

REM ✅ Étape 2 : Activer l’environnement virtuel
call venv\Scripts\activate.bat

REM ✅ Étape 3 : Installer les dépendances
echo 📦 Installation des dépendances (requirements.txt)...
pip install -r requirements.txt

REM ✅ Étape 4 : Lancer le backend Flask
echo 🔁 Lancement du serveur backend (Flask)...
start cmd /k " python app.py"

REM ✅ Étape 5 : Lancer le frontend dans le navigateur
echo 🌐 Ouverture de l'interface frontend...
start http://127.0.0.1:5000

exit
