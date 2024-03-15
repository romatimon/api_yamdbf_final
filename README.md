# Api_Yamdb

## Описание
Проект YaMDb собирает отзывы пользователей на различные произведения.
Произведения делятся на категории и жанры. Пользователи могут оставлять
свои отзывы и ставить оценки произведениям и комментировать отзывы других пользователей.

## Запуск проекта
- Клойнируйте репозиторий и перейдите в него
```
git clone https://github.com/Kobzar-sys/api_yamdb.git
cd api_yamdb
```
- Установите и активируйте виртуальное окружение
```
python -m venv venv
source venv/scripts/activate
``` 
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Выполните миграции:
```
python manage.py makemigrations
python manage.py migrate
```
- Загрузите в БД тестовые записи (опционально):
```
python manage.py load_base
```
- В папке с файлом manage.py выполните команду:
```
python manage.py runserver
```

## Примеры запросов к API и ответов от сервера

- Пример POST-запроса на адрес 
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/ 
для добавления отзыва: 
```
{
    "text": "Интересная книга!",
    "score": 8
}
```

Пример ответа:

```
{
    "id": 1,
    "text": "Интересная книга!",
    "author": "natalya",
    "score": 8,
    "pub_date": "2023-05-27T14:15:22Z"
}
```
- GET-запрос на адрес http://127.0.0.1:8000/api/v1/users/{username}/ для получения пользователя по username.

Пример ответа:

```
{
    "username": "string",
    "email": "user@example.com",
    "first_name": "string",
    "last_name": "string",
    "bio": "string",
    "role": "user"
}
```

## Документация
- Документация к API доступна после запуска проекта по ссылке: http://127.0.0.1:8000/redoc/

## Технологии
-Python
-Django
-Django Rest Framework 3.12.4
-Simple JWT
-SQLite3

### Авторы
- Дмитрий Кобзарь (тимлид), github: https://github.com/Kobzar-sys
- Анастасия Кудрявцева, github: https://github.com/np-dvs
- Роман Тимонин, github: https://github.com/romatimon
