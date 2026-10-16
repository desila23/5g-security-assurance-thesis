#!/bin/bash
cd -- "$(dirname -- "$0")"
python3 build.py
read -r -p "Premi Invio per chiudere."
