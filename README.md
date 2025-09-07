# ads-board

## Дипломная работа "Доска объявлений"
### Описание задачи:
Необходимо разработать backend-часть для сайта объявлений.  
Бэкенд-часть проекта предполагает реализацию следующего функционала:
- Авторизация и аутентификация пользователей.
- Распределение ролей между пользователями (пользователь и админ).
- Восстановление пароля через электронную почту.
- CRUD для объявлений на сайте.
- Под каждым объявлением пользователи могут оставлять отзывы.
- В заголовке сайта можно осуществлять поиск объявлений по названию.

---

# Деплой на удаленный сервер
### Первичная подготовка сервера (Ubuntu):
- Обновите дистрибутив ОС
```commandline
sudo apt update
sudo apt upgrade
```
- Настройте сетевой экран
```commandline
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
```
- Установите docker следуя инструкциям из официальной документации:  
https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
- Установите docker-compose
```commandline
apt install docker-compose
```
- Создайте нового пользователя для деплоя и запуска WEB приложения и добавьте его в группу docker:
```commandline
adduser <имя_пользователя>
sudo usermod -aG docker <имя_пользователя>
```
- Сгенерируйте ключ для доступа по ssh
```commandline
ssh-keygen -t ed25519 -f <имя_ключа>
```
публичную часть добавьте к authorized_keys пользователя на удаленном сервере, а приватную в переменные Actions secrets and variables для github action 

### CI/CD github actions
При событиях [push, pull_request] в репозитории, запускается CI/CD github actions у которого последовательно выполняются стадии:
- lint (линтер flake8)
- test (pytest django)
- build (сборка контейнера приложения и публикация в https://hub.docker.com/r/arsenty123321/ads-board/tags) 
- deploy (деплой кода на сервер, сборка и перезапуск контейнеров)

# Запуск с помощью docker-compose (локальная разработка)
## Настройка окружения и запуск с помощью docker-compose
#### Установка компонентов
- Установите docker для вашего дистрибутива ОС
- Установите docker-compose

#### Настройте переменные окружения:
- Необходимо создать файл .env на основе .env.sample и заполнить значения переменных

#### Запуск проекта со сборкой контейнера:
При сборке локально укажите название образа в .env:  
`BACKEND_DOCKER_IMAGE = "backend"`

```
docker-compose up --build
```
При выполнении команды произойдет сборка контейнера backend, инициализация WEB приложения и БД.

#### Проверка работоспособности сервисов:
- backend:
```
# Зайдите в браузере по URL и авторизируйтесь как супер-пользователь:
http://localhost:80/admin/

# Зайдите в браузере по URL:
http://localhost:80/swagger/

# Для отображения лога в консоли выполните команду:
docker-compose logs -f backend
```

- nginx
```
# Для отображения лога в консоли выполните команду:
docker-compose logs nginx
```

- db
```
# Выполните команду подставив реальные значения:
docker-compose exec db pg_isready -d [POSTGRES_DB] -U [POSTGRES_USER]

# Для отображения лога в консоли выполните команду:
docker-compose logs -f db
```

- redis
```
# Выполните команду:
docker-compose exec redis redis-cli ping

# Для отображения лога в консоли выполните команду:
docker-compose logs -f redis
```

- celery
```
# Для отображения лога в консоли выполните команду:
docker-compose logs -f celery
```

#### Сборка новой локальной версии контейнера приложения:
Команда сборки docker образа локально
```
docker build -t backend_image:latest .
```

# Локальная разработка (без docker)
## Настройка окружения для запуска на хосте
#### Предварительные требования
- Python 3.11
- PostgreSQL >=14
- Redis >= 5.0.7

#### Настройка окружения
- Выполнить команды:
```
# Подготовка окружения
pip install poetry
poetry install --no-root

# Настройка БД PostgreSQL:
# Создать пользователя для работы с БД
sudo -u postgres psql -c "
CREATE USER [имя_пользователя] WITH ENCRYPTED PASSWORD '[пароль]';
"

# Создать БД
sudo -u postgres psql -c "CREATE DATABASE ads-board;"

# Настроить доступ к БД для пользователя
sudo -u postgres psql -c "
ALTER DATABASE mailer OWNER TO [имя_пользователя];
GRANT ALL PRIVILEGES ON DATABASE ads-board TO [имя_пользователя];
"
```
- Создать файл .env на основе .env.sample и заполнить значения переменных
- Запустить миграции для подготовки проекта:
```
# Запуск миграций
poetry run ./manage.py migrate
```

- Создать пользователя для администрирования через WEB-UI:
```
# Создание администратора через кастомную команду
# логин и пароль задается в .env файле

poetry run ./manage.py csu

```

### Запуск проекта
```
# Запуск сервера
poetry run ./manage.py runserver
```

### Запуск тестов
```
# Запуск тестов со сбором покрытия
poetry run coverage run --source='.' manage.py test
# Генерация отчета покрытия тестами
poetry run coverage report
```

### Запуск celery воркера (Linux)
```
celery -A config worker --loglevel=info
```
