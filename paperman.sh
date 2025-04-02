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

python manage.py runserver 0.0.0.0:8090
