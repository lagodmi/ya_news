import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_homepage_news_count(client, news_for_home_page):
    """Проверка количества новостей на главной страницы."""
    url = reverse('news:home',)
    response = client.get(url)
    news_count = len(response.context['object_list'])
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorting(client, news_for_home_page):
    """Тест сортировки новостей."""
    url = reverse('news:home',)
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db 
def test_coments_sorting(client, news, coments_for_news):
    """Тест сортировки комментариев."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    context_news = response.context['news']
    all_comments = context_news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    """Анонимному недоступна форма для отправки комментария."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    """Авторизированному доступна форма для отправки комментария"""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
