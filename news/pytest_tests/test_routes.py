import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """
    Тест: анонимному пользователю доступны страницы:
    главная, регистрации пользователей, входа в учетную запись
    и выхода из нее
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_page_news_detail_availability_for_anonymous_user(client, news):
    """Тест: страница отдельной новости доступна анонимному пользователю"""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """
    Тест: страницы редактирования и удаления комментария доступны
    для автора комментария и недоступны для другого авторизованного
    пользователя
    """
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name', ('news:edit', 'news:delete')
)
def test_redirects(client, name, comment):
    """Тест: при попытке перехода на страницу редактирования или
    удаления комментария анонимный пользователь перенаправляется
    на страницу авторизации
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
