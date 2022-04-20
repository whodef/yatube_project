# Базовые команды и настройка проекта

Форматирование кода
- MacOS: `Option + Command + L`
- Windows: `Ctrl + Alt + I`
- Linux (PyCharm): `Ctrl + Alt + Shift + L`

Запуск сервера
`python3 manage.py runserver`

Создание виртуального окружения
`python3 -m venv venv`

Запуск виртуального окружения проекта
- В Windows: `.\venv\Scripts\activate`
- В MacOS или Linux: `source venv/bin/activate`

Остановка виртуального окружения
`deactivate`

Установка pytest и запуск тестов
`pip install -U pytest`

Обновить менеджер пакетов pip
`python3 -m pip install --upgrade pip`

Установка Django версии 2.2.19
`pip install Django==2.2.19`

Генерация SSH ключа
`ssh-keygen -t rsa -b 4096 -C "email@email.com"`

`pip freeze > requirements.txt`

При клонировании репозитория на другой компьютер или сервер выполните 
(предварительно создав и активировав нужное виртуальное окружение):
`pip install -r requirements.txt`

Создать базовую структуру проекта
`django-admin startproject yatube` или `python3 -m django startapp yatube`

Создать миграцию
`python manage.py makemigrations`
Например: `python manage.py makemigrations posts`

Запустить все миграции
`python manage.py migrate`
Например: `python manage.py migrate posts`

Создать супер пользователя
`python manage.py createsuperuser`

Сборка всей статики
`python manage.py collectstatic --clear`
`python manage.py collectstatic`

Изображения
`pip install Pillow`
`pip install sorl-thumbnail`


## GIT
Добавить папку в игнор-лист гита командой из корневой директории проекта (а можно дописать gitignore руками)
`echo 'static' >> .gitignore`

Удалить папку из списка отслеживаемых файлов (staging area)
`git rm -r --cached static`

Добавить файл в гит
`git add .gitignore`

Зафиксировать изменения в новом коммите
`git commit -m 'Директория static добавлена в gitignore'`

Запушить
`git push`


## Shell

Запуск
`python3 manage.py shell`

```python
from django.test import Client
# Создаём объект класса Client(), эмулятор веб-браузера
>>> guest_client = Client()
# — Браузер, сделай GET-запрос к главной странице
>>> response = guest_client.get('/')
# Какой код вернула страница при запросе?
>>> response.status_code
200  # Страница работает: она вернула код 200
```
Дополнительная информация:
- `status_code` — содержит код ответа запрошенного адреса;
- `client` — объект клиента, который использовался для обращения;
- `content` — данные ответа в виде строки байтов;
- `context` — словарь переменных, переданный для отрисовки шаблона при вызове функции `render()`;
- `request` — объект `request`, первый параметр view-функции, обработавшей запрос;
- `templates` — перечень шаблонов, вызванных для отрисовки запрошенной страницы;
- `resolver_match` — специальный объект, соответствующий `path()` из списка urlpatterns

### Django Python Shell

`python3 manage.py shell`

```python
from posts.models import Post, User
Post.objects.all()
me = User.objects.get(pk=1)
new = Post.objects.create(author=me, text="Смотри, этот пост я создал через shell!")
new.save()
```


## Выборочный запуск тестов

Запустит все тесты проекта
`python3 manage.py test`

Запустит только тесты в приложении posts
`python3 manage.py test posts`

Запустит только тесты из файла test_urls.py в приложении posts
`python3 manage.py test posts.tests.test_urls`

Запустит только тесты из класса StaticURLTests для test_urls.py в приложении posts
`python3 manage.py test posts.tests.test_urls.StaticURLTests`

Запустит только тест test_homepage() из класса StaticURLTests для test_urls.py в приложении posts
`python3 manage.py test posts.tests.test_urls.StaticURLTests.test_homepage`

Coverage - показывает % покрытия тестами
```python
pip3 install coverage
coverage run --source='posts,users' manage.py test -v 2
coverage report
coverage html #  сохранить в виде HTML
coverage run #  отчёт будет перезаписан
```

## База Данных и ORM

Удаление объекта из базы
`new.delete()`

Увидеть SQL-запрос, который будет отправлен к базе используя метод .query
`print(Post.objects.filter(author=me).query)`

В Django ORM аналог команд WHERE выглядит так: указывается имя поля, затем два знака подчеркивания __, 
название фильтра и его значение: contains — поиск по тексту в поле text. «Найти пост, где в поле text есть слово
"oops" именно в таком регистре»
`Post.objects.filter(text__contains='again')`

exact — точное совпадение. «Найти пост, где поле id точно равно 1»
`Post.objects.filter(id__exact=1) или Post.objects.filter(id=1)`

in — вхождение в множество. «Найти пост, где значение поля id точно равно одному из значений: 1, 3 или 4»
`Post.objects.filter(id__in=[1, 3, 4])`

Если вместо списка будет передана строка, она разобьётся на символы:
`Post.objects.filter(text__in="oops")`

Операторы сравнения
```
gt — > (больше),
gte — => (больше или равно),
lt — < (меньше),
lte — <= (меньше или равно).

Post.objects.filter(id__gt=5)
```

Операторы сравнения с началом и концом строки startswith, endswith
«Найти посты, где содержимое поля text начинается со строки "Утромъ"»
`Post.objects.filter(text__startswith="Утромъ")`

range — вхождение в диапазон
```
import datetime

start_date = datetime.date(1890, 1, 1)
end_date = datetime.date(1895, 3, 31)
Post.objects.filter(pub_date__range=(start_date, end_date))
```

При работе с частями дат можно применять дополнительные суффиксы date, year,
month, day, week, week_day, quarter и указывать для них дополнительные условия:
```
import datetime

Post.objects.filter(pub_date__date=datetime.date(1890, 1, 1))
Post.objects.filter(pub_date__date__lt=datetime.date(1895, 1, 1))
Post.objects.filter(pub_date__year=1890)
Post.objects.filter(pub_date__month__gte=6)
Post.objects.filter(pub_date__quarter=1)
```

isnull — проверка на пустое значение.
`Post.objects.filter(pub_date__isnull=True)`

Объединение условий
Исключить данные из выборки можно методом exclude()

Сортировка и ограничение количества результатов
Увидеть SQL-запрос, который будет отправлен к базе используя метод .query
`print(Post.objects.order_by("-pub_date")[:11].query)`
`Post.objects.filter(text__startswith='Утромъ').order_by("-pub_date")[:2]`

## Отладочная информация

```
import logging

log = logging.getLogger('django.db.backends')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
```

## Загрузка связанных записей

Один запрос SQL. select_related делает всё одним запросом:
```
related = Post.objects.select_related('author').all()
for post in related:
    tmp = f"{post.text} Автор {post.author.username}"
```

Несколько запросов SQL: prefetch_related не загружает повторно нужные связанные данные:
```
related = Post.objects.prefetch_related('author').all()
for post in related:
    tmp = f"{post.text} Автор {post.author.username}"
```

## Агрегирующие функции в Django ORM

Метод count() - узнать количество
`Post.objects.filter(pub_date__month__gt=6, pub_date__year=1854).count()`

Правильный способ: этот код просит базу вернуть число
```
if User.objects.count():
    print("Пользователи есть")
```

Метод aggregate() отдает только значение, результат работы агрегирующей функции
```
from django.db.models import Max, Count
Post.objects.aggregate(Max("id"))
Post.objects.aggregate(Count("id"))
```

Связи между таблицами
```
leo = User.objects.get(id=2)
leo.posts.count()
```

Метод annotate() возвращает объекты и добавляет к ним новые свойства
Чтобы применить агрегирующие функции к связанным данным из других таблиц, 
запрос делается через аннотирование, методом annotate().
```
annotated_results = User.objects.annotate(posts_count = Count('posts'))
for item in annotated_results:
    ...     print(f"Постов у пользователя {item.username}: {item.posts_count}")
```


### Управление пользователями
```python3
from django.db import models
from django.forms import ModelForm
from django.views.generic import CreateView


    class Book(models.Model):
        name = models.CharField(max_length=100)
        isbn = models.CharField(max_length=100)
        pages = models.IntegerField(min_value=1)
    class BookForm(ModelForm):
        class Meta:
             model = Book
             fields = ['name', 'isbn', 'pages']
    class BookView(CreateView):
        form_class = BookForm
        success_url = "/thankyou" # куда переадресовать пользователя после успешной отправки формы
        template_name = "new_book.html
```        

new_book.html
```HTML
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <input type="submit" value="Отправить">
    </form>
```

urls.py
```python
    path("new_book/", views.BookView.as_view(), name="new_book")
```
