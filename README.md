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

## Структура

```text
custom_auth/       JWT, Cookies, OAuth, DTO и контроллеры
users/             User, UserToken и миграции
movies/            Movie, CRUD, сериализаторы и HTML
lab2/              настройки Django и маршруты проекта
manage.py          команды Django
docker-compose.yml инфраструктура PostgreSQL и приложения
```
