import os
from dotenv import load_dotenv

from src.api_handler import HeadHunterAPI
from src.db_utils import create_database, create_tables, insert_data_to_db
from src.user_interface import run_user_interface

# Список 10 целевых компаний (ID на hh.ru)
# Яндекс, Сбер, VK, Т-Банк, Альфа-Банк, X5 Tech, Магнит, Лаборатория Касперского, Авито, Ozon
EMPLOYER_IDS = [
    "1740",
    "3529",
    "15477",
    "78638",
    "80",
    "4233",
    "4934",
    "2180",
    "24442",
    "94323",
]


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

    for emp_id in EMPLOYER_IDS:
        emp_info = hh_api.get_employer_info(emp_id)
        if emp_info:
            employers_list.append(
                {"id": int(emp_id), "name": emp_info["name"], "url": emp_info["alternate_url"]}
            )

        items = hh_api.get_employer_vacancies(emp_id)
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
