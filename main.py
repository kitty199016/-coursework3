import os
import json
from dotenv import load_dotenv

from src.api_handler import HeadHunterAPI
from src.db_utils import create_database, create_tables, insert_data_to_db
from src.user_interface import run_user_interface

EMPLOYERS_NAME = [
    "Ozon Tech",
    "Sber",
    "Yandex",
    "Tinkoff",
    "VK"
]

with open('data/hh_vacancies.json', 'r', encoding='utf-8') as file:
    backup_json = json.load(file)

def main() -> None:
    """Главная точка входа проекта."""
    # Загружаем скрытые параметры из .env файла
    load_dotenv()

    db_name = os.getenv("DB_NAME", "hh_vacancies_db")
    db_params = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT"),
    }

    # 1. Создаем базу данных
    print(f"Проверка и инициализация базы данных '{db_name}'...")
    create_database(db_params, db_name)

    # Обновляем параметры подключения, указывая созданную БД
    db_params["database"] = db_name

    # 2. Создаем таблицы
    print("Создание таблиц 'employers' и 'vacancies'...")
    create_tables(db_params)

    # 3. Собираем данные по API
    print("Сбор данных с hh.ru через API...")
    hh_api = HeadHunterAPI()
    employers_list = []
    vacancies_list = []

    for emp_name in EMPLOYERS_NAME:
        emp_id = hh_api.get_employers_id_by_company_name(emp_name)
        if emp_id:
            #Получилось загрузить из hh.ru
            emp_info = hh_api.get_employer_info(emp_id)
            items = hh_api.get_employer_vacancies(emp_id)
        else:
            #Не получилось забрать данные из hh.ru, забираем из файла
            items = []
            emp_id = None
            emp_info = None
            for item in backup_json["items"]:
                if item["employer"]["name"] == emp_name:
                    items.append(item)
                    if not emp_id:
                        emp_id = item["employer"]["id"]
                        emp_info = item["employer"]

        if emp_info:
            employers_list.append(
                {"id": int(emp_id), "name": emp_info["name"], "url": emp_info["alternate_url"]}
            )

        for item in items:
            salary = item.get("salary")
            salary_from = salary.get("from") if salary else None
            salary_to = salary.get("to") if salary else None
            currency = salary.get("currency") if salary else None

            # Фильтруем только рублевые вакансии для корректного расчета AVG (опционально)
            if currency and currency != "RUR":
                continue

            vacancies_list.append(
                {
                    "id": int(item["id"]),
                    "employer_id": int(emp_id),
                    "name": item["name"],
                    "salary_from": salary_from,
                    "salary_to": salary_to,
                    "currency": currency,
                    "url": item["alternate_url"],
                }
            )

    # 4. Наполняем БД данными
    print(f"Запись данных в БД. Компаний: {len(employers_list)}, Вакансий: {len(vacancies_list)}...")
    insert_data_to_db(db_params, employers_list, vacancies_list)
    print("Данные успешно сохранены!")

    # 5. Запуск пользовательского консольного интерфейса
    run_user_interface(db_params)


if __name__ == "__main__":
    main()
