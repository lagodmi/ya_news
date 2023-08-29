from http import HTTPStatus

from django.urls import reverse
import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, client):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.pk,))
    client.post(url, data={'text': 'Текст комментария'})
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(news, author_client):
    """Авторизованный пользователь может отправить комментарий."""
    comment_text = 'Текст комментария'
    url = reverse('news:detail', args=(news.pk,))
    author_client.post(url, data={'text': comment_text})
    comments_count = Comment.objects.count()
    comment = Comment.objects.get()
    assert comments_count == 1
    assert comment.text == comment_text
    assert comment.news, news
    assert comment.author, author_client


def test_user_cant_use_bad_words(author_client, news):
    """Комментарий c запрещёнными словами вернёт ошибку."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()
    assert response.context['form'].errors['text'] == [WARNING]
    assert comments_count == 0


@pytest.mark.django_db
def test_authorized_user_cant_delete_comment(authorized_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', args=(comment.id,))
    response = authorized_client.delete(url)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can__delete_comment(news, author_client, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', args=(comment.id,))
    author_client.delete(url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_authorized_user_cant_edit_comment(news, author_client, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    new_comment_text = 'новый текст'
    url = reverse('news:edit', args=(news.pk,))
    response = author_client.post(url, data={'text': new_comment_text})
    news_url = reverse('news:detail', args=(news.id,))
    assert response.url == news_url + '#comments'
    comment.refresh_from_db()
    assert comment.text == new_comment_text


@pytest.mark.django_db
def test_author_can__edit_comment(news, authorized_client, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    comment_text = comment.text
    new_comment_text = 'новый текст'
    url = reverse('news:edit', args=(news.pk,))
    response = authorized_client.post(url, data={'text': new_comment_text})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
