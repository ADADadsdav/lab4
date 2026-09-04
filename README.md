# Movie API — лабораторная работа №4

Автоматизированное документирование REST API с использованием OpenAPI и Swagger UI. Проект продолжает лабораторную работу №3: сохраняет JWT-аутентификацию через Cookies, OAuth 2.0 через Яндекс, CRUD фильмов, пагинацию и Soft Delete.

## Цель работы

- генерировать OpenAPI-документацию автоматически из Python-кода;
- описывать контроллеры, DTO, параметры, ответы и ошибки;
- показывать в документации JWT/Cookie и OAuth 2.0 security schemes;
- использовать Swagger UI для проверки защищённых endpoint-ов;
- отключать документацию в production.

## OpenAPI и Swagger

Документация генерируется code-first библиотекой `drf-spectacular`. Ручные YAML/JSON-описания API не используются.

В режиме разработки доступны:

- Swagger UI: http://localhost:4200/api/docs/
- OpenAPI schema: http://localhost:4200/api/schema/

При `APP_ENV=production` эти маршруты не регистрируются и возвращают `404 Not Found`.

Для проверки схемы:

```bash
python manage.py spectacular --file schema.yml --validate
```

## Что документировано

- все Auth endpoint-ы: регистрация, login, refresh, whoami, logout, logout-all и сброс пароля;
- OAuth 2.0 Authorization Code flow через Яндекс;
- CRUD фильмов: GET, POST, PUT, PATCH и DELETE;
- группы endpoint-ов `Auth`, `OAuth 2.0` и `Movies`;
- параметры `page`, `limit` и идентификатор фильма;
- DTO запросов и ответов с типами и примерами;
- ответы 200, 201, 204, 400, 401, 403 и 404;
- схема `CookieAuth` для JWT в HttpOnly cookie `access_token`;
- схема `YandexOAuth2` с authorization и token URL.

## Безопасность приложения

- bcrypt-пароли с уникальной солью;
- Access/Refresh Token с индивидуальной солью хеша в БД;
- HttpOnly и SameSite Cookies;
- middleware проверки JWT и отзыва токенов;
- CSRF Middleware Django;
- OAuth `state` для защиты от CSRF;
- проверка владельца фильма;
- Soft Delete;
- технические ошибки не возвращаются клиенту;
- секреты находятся в `.env`, а `.env` исключён из Git.

## API

| Метод | URL | Доступ |
|---|---|---|
| POST | `/auth/register` | Public |
| POST | `/auth/login` | Public, устанавливает Cookies |
| POST | `/auth/refresh` | Public, нужен Refresh Cookie |
| GET | `/auth/whoami` | CookieAuth |
| POST | `/auth/logout` | CookieAuth |
| POST | `/auth/logout-all` | CookieAuth |
| GET | `/auth/oauth/yandex` | Public |
| GET | `/auth/oauth/yandex/callback` | Public |
| POST | `/auth/forgot-password` | Public |
| POST | `/auth/reset-password` | Public |
| GET/POST | `/api/movies/` | CookieAuth |
| GET/PUT/PATCH/DELETE | `/api/movies/{id}/` | CookieAuth и проверка владельца |

## Переменные окружения

Скопируйте `.env.example` в `.env` и укажите:

- `SECRET_KEY`;
- `APP_ENV=development` или `APP_ENV=production`;
- `JWT_ACCESS_SECRET` и `JWT_REFRESH_SECRET`;
- параметры PostgreSQL;
- `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET`, `YANDEX_CALLBACK_URL`.

Файл `.env` не добавляется в репозиторий. В development документация включена, в production должна быть отключена.

## Запуск через Docker

```bash
docker compose up --build
docker compose exec app python manage.py migrate
```

Приложение доступно по адресу http://localhost:4200/.

Swagger UI открывается по адресу http://localhost:4200/api/docs/.

Docker-ресурсы лабораторной изолированы: используются контейнеры `lab4_app`, `lab4_postgres`, отдельная сеть `lab4_network` и отдельный volume базы данных.

## Локальный запуск

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

## Проверка

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py spectacular --file schema.yml --validate
.\.venv\Scripts\python.exe manage.py test
```

Перед защищёнными запросами в Swagger UI выполните `/auth/login`. Браузер сохранит HttpOnly Cookies, после чего можно проверять `/auth/whoami` и CRUD фильмов. Без авторизации защищённые методы должны возвращать `401`.

## Технический стек

- Python 3.13;
- Django 6.0.3;
- Django REST Framework 3.16.1;
- drf-spectacular 0.30.0 для автоматической OpenAPI-документации;
- PostgreSQL 16;
- PyJWT для JWT;
- bcrypt для хеширования паролей;
- requests для OAuth 2.0 через Яндекс;
- Docker и Docker Compose;
- Swagger UI для интерактивной проверки API.

## Проверка API через cURL

Команды выполняются после запуска приложения. Для Linux/macOS используйте Bash, для Windows удобнее выполнять команды в Git Bash.

### Регистрация

```bash
curl -X POST http://localhost:4200/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "confirm_password": "SecurePass123"
  }'
```

### Вход в систему

Сохраните Cookies, чтобы использовать их в защищённых запросах:

```bash
curl -X POST http://localhost:4200/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "password": "SecurePass123"
  }' \
  -c cookies.txt
```

### Проверка текущего пользователя

```bash
curl -i http://localhost:4200/auth/whoami \
  -b cookies.txt
```

Ожидаемый ответ: `200 OK`.

### Проверка защищённого endpoint без авторизации

```bash
curl -i http://localhost:4200/api/movies/
```

Ожидаемый ответ: `401 Unauthorized`.

### Получение списка фильмов

```bash
curl -i "http://localhost:4200/api/movies/?page=1&limit=10" \
  -b cookies.txt
```

### Создание фильма с авторизацией

```bash
curl -X POST http://localhost:4200/api/movies/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "Начало",
    "director": "Кристофер Нолан",
    "year": 2010
  }'
```

Скопируйте `id` из ответа и замените `MOVIE_ID` в следующих командах.

### Получение фильма по ID

```bash
curl -i http://localhost:4200/api/movies/MOVIE_ID/ \
  -b cookies.txt
```

### Полное обновление фильма — PUT

```bash
curl -X PUT http://localhost:4200/api/movies/MOVIE_ID/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "Интерстеллар",
    "director": "Кристофер Нолан",
    "year": 2014
  }'
```

### Частичное обновление фильма — PATCH

```bash
curl -X PATCH http://localhost:4200/api/movies/MOVIE_ID/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title": "Интерстеллар: обновлено"}'
```

### Мягкое удаление фильма — DELETE

```bash
curl -i -X DELETE http://localhost:4200/api/movies/MOVIE_ID/ \
  -b cookies.txt
```

Ожидаемый ответ: `204 No Content`.

### Обновление пары токенов — Refresh

```bash
curl -i -X POST http://localhost:4200/auth/refresh \
  -b cookies.txt \
  -c cookies.txt
```

### Выход из текущей сессии — Logout

```bash
curl -i -X POST http://localhost:4200/auth/logout \
  -b cookies.txt \
  -c cookies.txt
```

### Выход из всех сессий — Logout All

Сначала выполните вход ещё раз:

```bash
curl -i -X POST http://localhost:4200/auth/logout-all \
  -b cookies.txt \
  -c cookies.txt
```

### Вход через Яндекс OAuth 2.0

Откройте в браузере:

```text
http://localhost:4200/auth/oauth/yandex
```

Для работы нужны реальные `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET` и callback URL в `.env`.

### Запрос сброса пароля

```bash
curl -X POST http://localhost:4200/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

В development токен выводится в консоль приложения.

### Установка нового пароля

Замените `TOKEN_FROM_APPLICATION_CONSOLE` на токен из консоли:

```bash
curl -X POST http://localhost:4200/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_FROM_APPLICATION_CONSOLE",
    "new_password": "AnotherPass123",
    "confirm_password": "AnotherPass123"
  }'
```

## Автоматические проверки проекта

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py spectacular --file schema.yml --validate
.\.venv\Scripts\python.exe manage.py test
```

Проверяются регистрация, вход, Cookies, `/whoami`, ответы `401` и `403`, создание и владение фильмами, logout, OAuth `state`, соли паролей и токенов, сброс пароля и валидность OpenAPI-схемы.

## Структура

```text
custom_auth/       JWT, Cookies, OAuth, DTO и контроллеры
users/             User, UserToken и миграции
movies/            Movie, CRUD, сериализаторы и HTML
lab2/              настройки Django и маршруты проекта
manage.py          команды Django
docker-compose.yml инфраструктура PostgreSQL и приложения
```
