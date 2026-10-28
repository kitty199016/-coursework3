import pytest
from unittest.mock import patch, MagicMock
from src.api_handler import HeadHunterAPI


@pytest.fixture
def api_client() -> HeadHunterAPI:
    """Фикстура для инициализации клиента API."""
    return HeadHunterAPI()


@patch("requests.get")
def test_get_employer_info_success(mock_get: MagicMock, api_client: HeadHunterAPI) -> None:
    """Тест успешного получения информации о работодателе."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "1740", "name": "Яндекс", "alternate_url": "https://hh.ru"}
    mock_get.return_value = mock_response

    result = api_client.get_employer_info("1740")

    assert result["name"] == "Яндекс"
    assert result["id"] == "1740"
    mock_get.assert_called_once_with("https://hh.ru", headers=api_client._HeadHunterAPI__headers)


@patch("requests.get")
def test_get_employer_info_failure(mock_get: MagicMock, api_client: HeadHunterAPI) -> None:
    """Тест поведения API при ошибке ответа сервера (например, 404)."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = api_client.get_employer_info("invalid_id")

    assert result == {}


@patch("requests.get")
def test_get_employer_vacancies_success(mock_get: MagicMock, api_client: HeadHunterAPI) -> None:
    """Тест успешного получения списка вакансий."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"id": "12345", "name": "Python Developer", "alternate_url": "https://hh.ru"}
        ]
    }
    mock_get.return_value = mock_response

    result = api_client.get_employer_vacancies("1740")

    assert len(result) == 1
    assert result[0]["name"] == "Python Developer"
