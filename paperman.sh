#!/bin/bash

if ! command -v python &> /dev/null
then
    if command -v conda &> /dev/null
    then
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate python
    else
        echo "Error: No python!"
        exit 1
    fi
fi

echo "http://localhost:8090"

python manage.py runserver 0.0.0.0:8090
