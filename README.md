
# Movie API — Лабораторная работа №4

Система управления фильмами с REST API, аутентификацией через JWT + OAuth2 (Яндекс), мягким удалением и полной документацией.

## OpenAPI / Swagger

Документация API генерируется автоматически из Django REST Framework-кода с помощью `drf-spectacular`.

- Swagger UI: http://localhost:4200/api/docs/
- OpenAPI schema: http://localhost:4200/api/schema/

Документация доступна только при `APP_ENV=development`. В production маршруты документации не регистрируются и возвращают 404.

В Swagger UI защищённые методы используют схему `CookieAuth`: сначала выполните `/auth/login`, после чего браузер автоматически отправит HttpOnly cookie. В схеме также описан OAuth 2.0 Authorization Code flow через Яндекс.

Схему можно проверить автоматически:

```bash
python manage.py spectacular --file schema.yml --validate
```

## 🔐 Реализованные механизмы безопасности

- **JWT токены**: Access Token (15 мин) и Refresh Token (7 дней)
- **HttpOnly Cookies**: Токены передаются только через защищённые cookies
- **Хеширование паролей**: bcrypt с уникальной солью для каждого пользователя
- **Хранение токенов**: Токены хешируются (SHA-256) перед сохранением в БД
- **Отзыв токенов**: Возможность logout и logout-all с инвалидацией токенов в БД
- **OAuth 2.0**: Авторизация через Яндекс (Authorization Code Grant)
- **CSRF защита**: Параметр state в OAuth, SameSite cookies
- **Владение ресурсами**: Пользователи могут редактировать/удалять только свои фильмы
- **Soft Delete**: Мягкое удаление пользователей и фильмов

## 🛠 Технологический стек

- **Backend:** Python 3.12 + Django 6.0.3
- **Database:** PostgreSQL 16
- **ORM:** Django ORM с кастомными менеджерами
- **API Framework:** Django REST Framework 3.16.1
- **Аутентификация:** JWT (PyJWT), bcrypt
- **OAuth:** Ручная реализация Яндекс ID
- **DevOps:** Docker & Docker Compose

## 📋 API Endpoints

### Аутентификация

| Метод | URI | Описание | Доступ |
|-------|-----|----------|--------|
| POST | `/auth/register` | Регистрация нового пользователя | Public |
| POST | `/auth/login` | Вход (установка cookies) | Public |
| POST | `/auth/refresh` | Обновление пары токенов | Public (требуется Refresh Cookie) |
| GET | `/auth/whoami` | Проверка статуса и данные пользователя | Private |
| POST | `/auth/logout` | Завершение текущей сессии | Private |
| POST | `/auth/logout-all` | Завершение всех сессий пользователя | Private |
| GET | `/auth/oauth/yandex` | Инициация входа через Яндекс | Public |
| GET | `/auth/oauth/yandex/callback` | Обработка ответа от Яндекса | Public |
| POST | `/auth/forgot-password` | Запрос на сброс пароля | Public |
| POST | `/auth/reset-password` | Установка нового пароля | Public |

### Фильмы (защищены авторизацией)

| Метод | URI | Описание | Доступ |
|-------|-----|----------|--------|
| GET | `/api/movies/` | Список фильмов с пагинацией | Private |
| GET | `/api/movies/{id}/` | Получить фильм по ID | Private (владелец) |
| POST | `/api/movies/` | Создать новый фильм | Private |
| PUT | `/api/movies/{id}/` | Полностью обновить фильм | Private (владелец) |
| PATCH | `/api/movies/{id}/` | Частично обновить фильм | Private (владелец) |
| DELETE | `/api/movies/{id}/` | Мягкое удаление фильма | Private (владелец) |

## 🚀 Быстрый старт

### 1. Запуск инфраструктуры

```bash
docker-compose up -d --build
```

### 2. Применение миграций

```bash
docker-compose exec app python manage.py makemigrations
docker-compose exec app python manage.py migrate
```

### 3. Доступ к приложению

- **API:** http://localhost:4200/api/movies/
- **Главная страница:** http://localhost:4200/

## 📝 Примеры запросов

### Регистрация пользователя

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

```bash
curl -X POST http://localhost:4200/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "password": "SecurePass123"
  }' \
  -c cookies.txt
```

### Создание фильма (с авторизацией)

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

### Проверка статуса авторизации

```bash
curl -X GET http://localhost:4200/auth/whoami \
  -b cookies.txt
```

## 🧪 Тестирование безопасности

1. **Уникальность хешей**: Зарегистрируйте двух пользователей с одинаковым паролем — хеши в БД будут разными
2. **Защита ресурсов**: Попробуйте получить доступ к `/api/movies/` без cookie — получите 401
3. **Владение ресурсом**: Пользователь не может удалить/редактировать чужие фильмы
4. **Истечение токена**: Через 15 минут access token истечёт, но refresh token позволит обновиться
5. **Logout**: После выхода токены инвалидируются в БД
6. **OAuth**: Вход через Яндекс работает с проверкой state (защита от CSRF)

## 📂 Структура проекта

```
lab2/
├── docker-compose.yml          # Конфигурация Docker
├── Dockerfile                   # Сборка образа приложения
├── requirements.txt             # Зависимости Python
├── manage.py                    # Управление Django проектом
├── .env                         # Переменные окружения (не в Git!)
├── custom_auth/                 # Модуль аутентификации
│   ├── auth_service.py           # Сервис аутентификации
│   ├── jwt_service.py            # Сервис JWT токенов
│   ├── oauth_service.py          # OAuth Яндекс
│   ├── middleware.py             # Промежуточное ПО
│   ├── serializers.py            # DTO и валидация
│   ├── views.py                  # Контроллеры
│   ├── urls.py                   # Маршруты
│   └── permissions.py            # Разрешения
├── users/                        # Модуль пользователей
│   ├── models.py                 # Модели User, UserToken
│   └── apps.py                   # Конфигурация
├── movies/                       # Модуль фильмов
│   ├── models.py                 # Модель Movie с soft delete
│   ├── views.py                  # API и HTML представления
│   ├── serializers.py            # Сериализаторы с валидацией
│   ├── services.py               # Сервисный слой
│   └── urls.py                   # Маршруты
└── lab2/                         # Конфигурация Django
    ├── settings.py               # Настройки
    └── urls.py                   # Главные маршруты
```
