import os
from src.db_manager import DBManager


def format_salary(salary_from: int, salary_to: int) -> str:
    """Форматирует вывод зарплаты в понятную строку."""
    if salary_from and salary_to:
        return f"от {salary_from} до {salary_to} руб."
    if salary_from:
        return f"от {salary_from} руб."
    if salary_to:
        return f"до {salary_to} руб."
    return "Не указана"


def run_user_interface(db_params: dict) -> None:
    """Запускает интерактивный текстовый интерфейс для работы с БД."""
    db_manager = DBManager(db_params)
    print("\nДобро пожаловать в менеджер вакансий HH.ru!")

    while True:
        print("\nДоступные действия:")
        print("1 - Показать список компаний и количество их вакансий")
        print("2 - Показать все вакансии")
        print("3 - Показать среднюю зарплату по вакансиям")
        print("4 - Показать вакансии с зарплатой выше средней")
        print("5 - Поиск вакансий по ключевому слову")
        print("0 - Выйти из программы")

        choice = input("\nВыберите действие (введите цифру): ").strip()

        if choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            print("\nСписок компаний:")
            for company, count in companies:
                print(f"• {company} — вакансий в базе: {count}")

        elif choice == "2":
            vacancies = db_manager.get_all_vacancies()
            print(f"\nВсего найдено вакансий: {len(vacancies)}")
            for comp, name, s_from, s_to, url in vacancies[:20]:  # Ограничим вывод для читаемости
                print(f"Компания: {comp} | Вакансия: {name} | ЗП: {format_salary(s_from, s_to)} | Ссылка: {url}")

        elif choice == "3":
            avg_sal = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата среди всех вакансий в базе: {avg_sal} руб.")

        elif choice == "4":
            high_vacancies = db_manager.get_vacancies_with_higher_salary()
            print(f"\nНайдено {len(high_vacancies)} вакансий с оплатой выше средней.")
            for comp, name, s_from, s_to, url in high_vacancies[:15]:
                print(f"Компания: {comp} | Вакансия: {name} | ЗП: {format_salary(s_from, s_to)} | Ссылка: {url}")

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска (например, python): ").strip()
            keyword_vacancies = db_manager.get_vacancies_with_keyword(keyword)
            print(f"\nНайдено вакансий по запросу '{keyword}': {len(keyword_vacancies)}")
            for comp, name, s_from, s_to, url in keyword_vacancies[:15]:
                print(f"Компания: {comp} | Вакансия: {name} | ЗП: {format_salary(s_from, s_to)} | Ссылка: {url}")

        elif choice == "0":
            print("\nПрограмма успешно завершена. Всего доброго!")
            db_manager.close()
            break
        else:
            print("\nОшибка: Некорректный ввод, попробуйте еще раз.")
