#!/bin/bash
# Выполняем скрипт каждые два часа
0 */2 * * * root /usr/local/bin/python /app/parser/main.py >> /var/log/cron.log 2>&1