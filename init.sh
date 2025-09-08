#!/bin/bash

# Миграции при запуске
if [ ! -f .migrated ]; then
  python ./manage.py migrate
fi

# Создать суперпользователя при первом запуске
if [ ! -f init/.superuser_created ]; then
  echo "Creating superuser..."
  python ./manage.py csu
  touch init/.superuser_created
fi

# Запуск основного приложения
exec sh -c 'python manage.py collectstatic -c --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000'