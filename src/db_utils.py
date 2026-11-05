from typing import Any, Dict, List
import psycopg2


def create_database(db_params: dict, db_name: str) -> None:
    """Автоматически создает новую базу данных PostgreSQL, если она не существует."""
    params = db_params.copy()
    params["database"] = "postgres"  # Подключаемся к системной БД для создания новой

    conn = psycopg2.connect(**params)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cur.fetchone()
        if not exists:
            cur.execute(f"CREATE DATABASE {db_name};")
    conn.close()


def create_tables(db_params: dict) -> None:
    """Создает таблицы employers и vacancies в целевой базе данных."""
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS vacancies CASCADE;")
        cur.execute("DROP TABLE IF EXISTS employers CASCADE;")

        cur.execute(
            """
            CREATE TABLE employers (
                employer_id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255)
            );
        """
        )

        cur.execute(
            """
            CREATE TABLE vacancies (
                vacancy_id INT PRIMARY KEY,
                employer_id INT REFERENCES employers(employer_id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                salary_from INT,
                salary_to INT,
                currency VARCHAR(10),
                url VARCHAR(255)
            );
        """
        )
    conn.commit()
    conn.close()


def insert_data_to_db(db_params: dict, employers_data: List[dict], vacancies_data: List[dict]) -> None:
    """Заполняет таблицы работодателей и вакансий собранными данными."""
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cur:
        for emp in employers_data:
            cur.execute(
                """
                INSERT INTO employers (employer_id, name, url)
                VALUES (%s, %s, %s) ON CONFLICT (employer_id) DO NOTHING;
            """,
                (emp["id"], emp["name"], emp["url"]),
            )

        for vac in vacancies_data:
            cur.execute(
                """
                INSERT INTO vacancies (vacancy_id, employer_id, name, salary_from, salary_to, currency, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (vacancy_id) DO NOTHING;
            """,
                (
                    vac["id"],
                    vac["employer_id"],
                    vac["name"],
                    vac["salary_from"],
                    vac["salary_to"],
                    vac["currency"],
                    vac["url"],
                ),
            )
    conn.commit()
    conn.close()
