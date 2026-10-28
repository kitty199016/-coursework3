import pytest
from unittest.mock import MagicMock, patch
from src.db_manager import DBManager


@pytest.fixture
def mock_db_params() -> dict:
    """Фикстура с фиктивными параметрами подключения."""
    return {
        "host": "localhost",
        "user": "test_user",
        "password": "test_password",
        "port": "5432",
        "database": "test_db"
    }


@patch("psycopg2.connect")
def test_get_companies_and_vacancies_count(mock_connect: MagicMock, mock_db_params: dict) -> None:
    """Тест метода получения количества вакансий компаний."""
    # Настраиваем фейковый курсор и его ответ
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("Яндекс", 10), ("Сбер", 5)]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    # Инициализируем менеджер и вызываем метод
    db_manager = DBManager(mock_db_params)
    result = db_manager.get_companies_and_vacancies_count()

    assert len(result) == 2
    assert result[0] == "Яндекс"
    assert result[1][1] == 5
    mock_cursor.execute.assert_called_once()


@patch("psycopg2.connect")
def test_get_avg_salary(mock_connect: MagicMock, mock_db_params: dict) -> None:
    """Тест метода расчета средней зарплаты."""
    mock_cursor = MagicMock()
    # Функция AVG в SQL возвращает одно значение внутри кортежа в списке: [(150000.0,)]
    mock_cursor.fetchall.return_value = [(150000.0,)]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager = DBManager(mock_db_params)
    result = db_manager.get_avg_salary()

    assert result == 150000.0


@patch("psycopg2.connect")
def test_get_vacancies_with_keyword(mock_connect: MagicMock, mock_db_params: dict) -> None:
    """Тест поиска вакансий по ключевому слову с передачей аргумента в SQL."""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("Яндекс", "Python Стажер", 50000, None, "http://link")]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager = DBManager(mock_db_params)
    result = db_manager.get_vacancies_with_keyword("python")

    assert len(result) == 1
    assert "Python" in result[0][1]

    # Проверяем, что в SQL-запрос корректно подставились проценты % для оператора LIKE/ILIKE
    called_args = mock_cursor.execute.call_args[0]
    assert called_args[1] == ("%python%",)
