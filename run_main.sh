#!/bin/bash
# Выполняем скрипт каждые часы
* * * * * root /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1
