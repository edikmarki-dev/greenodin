#!/bin/sh
# Повна збірка сайту у ../public (uk + /ru + /en). Запуск: sh generator/build.sh
set -e
export PYTHONHASHSEED=0   # однаковий результат при кожній збірці
cd "$(dirname "$0")"
rm -rf ../public
python3 gen.py
python3 i18n.py extract
python3 i18n.py build
cp build/site_index_full.html ../public/index.html
