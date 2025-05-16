#!/usr/bin/env bash
# exit on error
set -o errexit

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi
source .venv/Scripts/activate

# Install & Execute WebPack 
# npm i
# npm run build

# Install modules 
python -m pip install --upgrade pip
pip install wheel
pip install -r requirements.txt

# Collect Static
python manage.py collectstatic --no-input

# Migrate DB
python manage.py makemigrations
python manage.py migrate