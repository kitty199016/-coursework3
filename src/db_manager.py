from typing import Any, List, Tuple
import psycopg2


class DBManager:
    """Класс для подключения и выполнения аналитических запросов к СУБД PostgreSQL."""

    def __init__(self, db_params: dict) -> None:
        self.params = db_params
        self.conn = psycopg2.connect(**self.params)

    def _execute_select(self, query: str, params: Tuple[Any, ...] = None) -> List[Tuple[Any, ...]]:
        """Вспомогательный защищенный метод для чтения данных из БД."""
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Получает список всех компаний и количество вакансий у каждой компании."""
        query = """
            SELECT employers.name, COUNT(vacancies.vacancy_id) AS vacancy_count
            FROM employers
            LEFT JOIN vacancies USING(employer_id)
            GROUP BY employers.name
            ORDER BY vacancy_count DESC;
        """
        return self._execute_select(query)

    def get_all_vacancies(self) -> List[Tuple[str, str, int, int, str]]:
        """Получает список вакансий: название компании, вакансии, зарплата от/до и ссылка."""
        query = """
            SELECT employers.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
            FROM vacancies
            JOIN employers USING(employer_id);
        """
        return self._execute_select(query)

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям."""
        query = """
            SELECT AVG((COALESCE(salary_from, salary_to) + COALESCE(salary_to, salary_from)) / 2)
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
        """
        result = self._execute_select(query)
        if result and result[0][0] is not None:
            return round(float(result[0][0]), 2)
        return 0.0

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, int, int, str]]:
        """Получает список вакансий, у которых зарплата выше средней по всем вакансиям."""
        avg_salary = self.get_avg_salary()
        query = """
            SELECT employers.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
            FROM vacancies
            JOIN employers USING(employer_id)
            WHERE (COALESCE(salary_from, salary_to) + COALESCE(salary_to, salary_from)) / 2 > %s;
        """
        return self._execute_select(query, (avg_salary,))

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, int, int, str]]:
        """Получает список вакансий, в названии которых содержатся переданные слова (через LIKE/ILIKE)."""
        query = """
            SELECT employers.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
            FROM vacancies
            JOIN employers USING(employer_id)
            WHERE vacancies.name ILIKE %s;
        """
        return self._execute_select(query, (f"%{keyword}%",))

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()
