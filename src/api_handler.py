from typing import Any, Dict, List
import requests


class HeadHunterAPI:
    """Класс для работы с публичным API сайта hh.ru."""

    def __init__(self) -> None:
        self.__base_url = "https://api.hh.ru"
        self.__headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (kalinger90@list.ru)"}

    def get_employers_id_by_company_name(self, company_name: str) -> dict:
        """Получает employe_id по имени компании"""
        url = f"{self.__base_url}/employers"
        params = {
            "text": company_name,  # Название компании для поиска
            "per_page": 1  # Количество результатов в выдаче
        }
        response = requests.get(url, headers=self.__headers, params=params)
        if response.status_code == 200:
            return response.json()
        print(response.status_code, response.text)
        return {}

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
        response = requests.get(url, params=params, headers=self.__headers)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
