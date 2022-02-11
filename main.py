import os
import requests
import copy

from dotenv import load_dotenv
from itertools import count
from terminaltables import SingleTable


def collect_table(language, table, vacancies_by_languages):
    table_copy = copy.copy(table)
    if language in vacancies_by_languages:
        table_copy.append([
            language,
            vacancies_by_languages[language]['vacancies_found'],
            vacancies_by_languages[language]['vacancies_processed'],
            vacancies_by_languages[language]['average_salary']])
    return table_copy


def predict_rub_salary(vacancy_from, vacancy_to):
    if not vacancy_from:
        return int(vacancy_to * 0.8)
    if not vacancy_to:
        return int(vacancy_from * 1.2)
    return int((vacancy_from + vacancy_to) / 2)


def get_table(languages, title, lang):
    table = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата'],
    ]
    for language in languages:
        table = collect_table(
            language,
            table,
            lang)
    table_instance = SingleTable(table, title)
    return table_instance.table


def get_hh_statistic(languages):
    lang = {}
    for language in languages:
        lang[language] = get_hh_statistic_of_lang(
            language)
    return lang


def get_sj_statistic(languages, token):
    lang = {}
    for language in languages:
        lang[language] = get_sj_statistic_of_lang(
            language, token)
    return lang


def get_vacancies_statistic(vacancies_by_language, average_salary, vacancies_count):
    hh_vacancies_by_languages = {
        'vacancies_found': vacancies_by_language,
        'average_salary': average_salary,
        'vacancies_processed': vacancies_count}
    return hh_vacancies_by_languages


def get_hh_vacancies(language, page=0):
    hh_url = 'https://api.hh.ru/vacancies'
    param = {'specialization': '1.221',
             'area': '1',
             'text': language,
             'per_page': 100,
             'page': page}
    response = requests.get(hh_url, params=param)
    response.raise_for_status()
    programmer_vacancies_by_language = response.json()
    return programmer_vacancies_by_language


def get_hh_statistic_of_lang(language):
    number_of_professions = 0
    average_salary = 0
    hh_vacancies = get_hh_vacancies(language)
    for page in range(hh_vacancies['pages']):
        vacancies_by_page = get_hh_vacancies(language, page)
        for vacancy in vacancies_by_page['items']:
            salary_vacancy = vacancy['salary']
            if not salary_vacancy or salary_vacancy['currency'] != 'RUR':
                continue
            average_salary += predict_rub_salary(
                salary_vacancy['from'],
                salary_vacancy['to'])
            number_of_professions += 1
    if number_of_professions != 0:
        average_salary_for_profession = average_salary // number_of_professions
        vacancies_statistic = get_vacancies_statistic(
            hh_vacancies['found'],
            average_salary_for_profession,
            number_of_professions)
        return vacancies_statistic


def get_sj_vacancies(language, page=0):
    headers = {'X-Api-App-Id': sj_token}
    sj_url = 'https://api.superjob.ru/2.0/vacancies'
    sj_param = {'catalogues': 48,
                'town': 4,
                'keyword': language,
                'count': 20,
                'page': page}
    response = requests.get(sj_url, headers=headers, params=sj_param)
    response.raise_for_status()
    super_job = response.json()
    return super_job


def get_sj_statistic_of_lang(language):
    professions_sj_number = 0
    curuncy = 0
    page = 0
    iter_count = count(start=0, step=10)
    for number in iter_count:
        sj_vacancies = get_sj_vacancies(language, page)
        if sj_vacancies['objects']:
            for vacancy in sj_vacancies['objects']:
                if vacancy['currency'] == 'rub':
                    if vacancy['payment_from'] or vacancy['payment_to']:
                        curuncy += predict_rub_salary(
                            vacancy['payment_from'],
                            vacancy['payment_to'])
                        professions_sj_number += 1
            if not sj_vacancies['more']:
                break
            page += 1
        if professions_sj_number:
            average_salary_for_profession = curuncy // professions_sj_number
            vacancies_statistic = get_vacancies_statistic(
                sj_vacancies['total'],
                average_salary_for_profession,
                professions_sj_number)
            return vacancies_statistic


if __name__ == '__main__':
    load_dotenv()
    sj_token = os.getenv('SUPERJOB_TOKEN')
    hh_title = 'HeadHunter Moscow'
    sj_title = 'SuperJob Moscow'
    languages = ['CSS',
                 'JavaScript',
                 'Java'
                 'C#',
                 'Ruby',
                 'PHP',
                 'C++',
                 'Python']
    print(get_table(languages, hh_title, get_hh_statistic(languages)))
    print(get_table(languages, sj_title, get_sj_statistic(
        languages,
        sj_token)))
