from typing import Any, Dict, List
import requests


class HeadHunterAPI:
    """Класс для работы с публичным API сайта hh.ru."""

    def __init__(self) -> None:
        self.__base_url = "https://hh.ru"
        self.__headers = {"User-Agent": "HH-Database-App/1.0 (contacts@example.com)"}

    def get_employer_info(self, employer_id: str) -> Dict[str, Any]:
        """Получает информацию о конкретном работодателе по его ID."""
        url = f"{self.__base_url}/employers/{employer_id}"
        response = requests.get(url, headers=self.__headers)
        if response.status_code == 200:
            return response.json()
        return {}

    def get_employer_vacancies(self, employer_id: str) -> List[Dict[str, Any]]:
        """Получает список вакансий компании (до 100 штук) по ID работодателя."""
        url = f"{self.__base_url}/vacancies"
        params = {"employer_id": employer_id, "per_page": 100}
        response = requests.get(url, params=params, headers=headers=self.__headers)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
