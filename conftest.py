from django.conf import settings
from datetime import datetime, timedelta
import pytest
import pytz
from news.models import News, Comment


@pytest.fixture
def authorized_client(django_user_model, client):
    user = django_user_model.objects.create(username='Юзер')
    client.force_login(user)
    return client


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def news_for_home_page():
    today = datetime.today()
    news = News.objects.bulk_create([
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])
    return news


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news, author=author, text='Tекст',
    )


@pytest.fixture
def coments_for_news(author, news):
    timezone = pytz.timezone('Europe/Moscow')
    now = datetime.now(timezone)
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment
