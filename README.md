# Блог для публикации футбольных новостей FootNews
## Функционал:
- Позволяет публиковать записи и оставлять комментарии под ними
- Есть возможность подписаться на автора и видеть все его записи в отдельной вкладке
- После регистрации создаётся отдельная страница, со всеми записями автора
- Можно создавать группы, для них появляется отдельная страница
- Интерфейс администратора

# Подготовка рабочей среды
Перейдите в свою рабочую директорию и выполните следующие команды:
```
git clone https://github.com/avcherezov/yatube.git
cd yatube
```
Создайте и активируйте виртуальное окружение:
```
source -m venv venv
source venv/Scripts/activate
```
Установите необходимые зависимости:
```
pip install -r requirements.txt
```
Выполните миграции:
```
python manage.py migrate
```
Создайте суперпользователя:
```
python manage.py createsuperuser
```
Запустите сервер разработки:
```
python manage.py runserver
```

# Стэк
<<<<<<< HEAD
Django, Django ORM, Pytest, Pillow, Gunicorn, Nginx, PostgreSQL, Яндекс.Облако
=======
Django, Django ORM, Pytest, Pillow, Gunicorn, Nginx, PostgreSQL, Яндекс.Облако
>>>>>>> c99ae5cebbadc9f13806096bb8df06f26cf205bc
