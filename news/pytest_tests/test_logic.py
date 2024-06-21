import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse
from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    """Тест: анонимный пользователь не может оставить комментарий"""
    url = reverse('news:detail', args=(news.pk,))
    comments_count_before = Comment.objects.count()
    response = client.post(url, form_data)
    comments_count_after = Comment.objects.count()
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert comments_count_before == comments_count_after


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
        author_client, author, form_data, news):
    """Тест: авторизованный пользователь может оставить комментарий"""
    url = reverse('news:detail', args=(news.pk,))
    comments_count_before = Comment.objects.count()
    response = author_client.post(url, form_data)
    comments_count_after = Comment.objects.count()
    comment = Comment.objects.get()
    success_url = reverse('news:detail', args=(news.pk,)) + '#comments'
    assert comments_count_after == comments_count_before + 1
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author
    assertRedirects(response, success_url)


@pytest.mark.django_db
def test_author_can_edit_delete_comment(
        author_client, comment, news):
    """
    Тест: авторизованный пользователь может
    редактировать или удалять свои комментарии
    """
    url = reverse('news:delete', args=(comment.pk,))
    comments_count_before = Comment.objects.count()
    response = author_client.post(url)
    comments_count_after = Comment.objects.count()
    success_url = reverse('news:detail', args=(news.pk,)) + '#comments'
    assert comments_count_after == comments_count_before - 1
    assertRedirects(response, success_url)


@pytest.mark.django_db
def test_not_author_cant_edit_delete_comment(
        not_author_client, comment):
    """
    Тест: авторизованный пользователь не может
    редактировать или удалять чужие комментарии
    """
    url = reverse('news:delete', args=(comment.pk,))
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(url)
    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_after == comments_count_before


def test_user_cant_use_bad_words(not_author_client, news):
    """
    Тест: если комментарий содержит запрещенные слова,
    то он не будет опубликован, а форма вернет ошибку
    """
    url = reverse('news:detail', args=(news.pk,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
