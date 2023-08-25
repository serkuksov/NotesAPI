# Проект "Заметки пользователей"

<img alt="Проект &quot;Заметки пользователей&quot;" src="images/note.png" width="150"/>

## Описание проекта

Проект "Заметки пользователей" - это веб-приложение, разработанное с использованием FastAPI, SQLAlchemy и PostgreSQL, которое предоставляет пользователям возможность создавать, редактировать, просматривать и управлять своими заметками. Особенностью проекта является поддержка аутентификации через JSON Web Tokens (JWT), а также дополнительные функции фильтрации, сортировки и поиска для удобства пользователей.

## Функциональность

- **Аутентификация и Регистрация**: Пользователи могут зарегистрироваться, а также войти в систему с помощью JSON Web Tokens (JWT), обеспечивая безопасное взаимодействие.

- **Создание и Управление Заметками**: Пользователи могут создавать заметки, вносить изменения, а также удалять ненужные записи.

- **Фильтрация**: Возможность фильтрации заметок по названию, а так же по части имени пользователя, что позволяет легко находить заметки конкретных авторов.

- **Сортировка**: Возможность сортировки по дате создания и названию заметки, как в возрастающем, так и в убывающем порядке.

- **Поиск**: Пользователи могут осуществлять поиск по части названия и содержания заметок для быстрого нахождения нужной информации.

- **Пагинация**: Длинные списки заметок разбиваются на страницы для удобства навигации и быстрой загрузки.

## Технологии

- Backend: FastAPI (Python)
- База данных: PostgreSQL с использованием SQLAlchemy
- Аутентификация: JSON Web Tokens (JWT)

## Установка и Запуск

1. Склонируйте репозиторий:

```shell
git clone https://github.com/serkuksov/NotesAPI
```

2. Запустите приложение в Docker контенере:

```shell
docker-compose up --build
```

3. Перейдите в браузере по адресу http://localhost:8000 для начала работы с приложением.

## Документация

API приложения документировано встроенной документацией FastAPI. Чтобы получить доступ к документации, запустите сервер и перейдите по адресу http://localhost:8000/docs.

## Переменные окружения

В процессе деплоя на реальный сервер необходимо настроить некоторые переменные окружения в файле `.env`, чтобы обеспечить корректное функционирование приложения:

- `SECRET_KEY`: Секретный ключ приложения для обеспечения безопасности.
- `DB_HOST`: Хост базы данных (при использовании базы данных из контейнера не меняется, по умолчанию название контейнера db)
- `DB_PORT`: Порт базы данных (при использовании базы данных из контейнера не меняется, по умолчанию 5432)
- `DB_NAME`: Имя базы данных.
- `DB_USER`: Пользователь базы данных.
- `POSTGRES_PASSWORD`: Пароль для доступа к базе данных PostgreSQL.

## Обратная Связь

Если вы нашли ошибку, хотите добавить новую функциональность или улучшить существующую, не стесняйтесь создавать Pull Request.

Если у вас есть вопросы или предложения, вы можете связаться со мной по электронной почте: ser.kuksov@mail.ru.

**Автор:** Куксов Сергей
**Лицензия:** MIT
