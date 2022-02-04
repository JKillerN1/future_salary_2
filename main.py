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


def get_statistic_for_hh(languages, hh_title):
    lang = {}
    hh_vacancies_by_languages = {}
    hh_table = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата'],
    ]
    for language in languages:
        lang[language] = get_statistic_of_lang_hh(
            language,
            hh_vacancies_by_languages)
        hh_table = collect_table(
            language,
            hh_table,
            hh_vacancies_by_languages)

    table_instance = SingleTable(hh_table, hh_title)
    return table_instance.table


def get_statistic_of_lang_hh(language, hh_vacancies_by_languages):
    hh_url = 'https://api.hh.ru/vacancies'
    number_of_professions = 0
    average_salary = 0
    param = {'specialization': '1.221',
             'area': '1',
             'text': language,
             'per_page': 100}
    response = requests.get(hh_url, params=param)
    response.raise_for_status()
    proggramer_vacancies_by_language = response.json()
    for page in range(proggramer_vacancies_by_language['pages']):
        param['page'] = page
        page_response = requests.get(hh_url, params=param)
        page_response.raise_for_status()
        vacancies_by_page = page_response.json()
        for vacancy in vacancies_by_page['items']:
            salary_vacancy = vacancy['salary']
            if not salary_vacancy or salary_vacancy['currency'] != 'RUR':
                continue
            average_salary += predict_rub_salary(
                salary_vacancy['from'],
                salary_vacancy['to'])
            number_of_professions += 1

    if number_of_professions != 0:
        hh_vacancies_by_languages[language] = {
            'vacancies_found': proggramer_vacancies_by_language['found'],
            'average_salary': average_salary // number_of_professions,
            'vacancies_processed': number_of_professions}
        return hh_vacancies_by_languages[language]


def get_statistic_for_sj(languages, sj_title, sj_token):
    sj_lang = {}
    sj_vacancies_by_languages = {}
    sj_table = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата'],
    ]
    for language in languages:
        sj_lang[language] = get_statistic_of_lang_sj(
            language,
            sj_vacancies_by_languages,
            sj_token)
        sj_table = collect_table(
            language,
            sj_table,
            sj_vacancies_by_languages)
    table_instance = SingleTable(sj_table, sj_title)
    return table_instance.table


def get_statistic_of_lang_sj(language, sj_vacancies_by_languages, sj_token):
    headers = {'X-Api-App-Id': sj_token}
    sj_url = 'https://api.superjob.ru/2.0/vacancies'
    professions_sj_number = 0
    curuncy = 0
    sj_param = {'catalogues': 48,
                'town': 4,
                'keyword': language,
                'count': 20,
                'page': 0}
    iter_count = count(start=0, step=10)
    for number in iter_count:
        response = requests.get(sj_url, headers=headers, params=sj_param)
        response.raise_for_status()
        super_job = response.json()
        if super_job['objects']:
            for vacancy in super_job['objects']:
                if vacancy['currency'] == 'rub':
                    if vacancy['payment_from'] or vacancy['payment_to']:
                        curuncy += predict_rub_salary(
                            vacancy['payment_from'],
                            vacancy['payment_to'])
                        professions_sj_number += 1
            if not super_job['more']:
                break
            sj_param['page'] += 1
        if professions_sj_number:
            sj_vacancies_by_languages[language] = {
                'vacancies_found': super_job['total'],
                'average_salary': curuncy // professions_sj_number,
                'vacancies_processed': professions_sj_number
            }
            return sj_vacancies_by_languages[language]


if __name__ == '__main__':
    load_dotenv()
    sj_token = os.getenv('SUPERJOB_TOKEN')
    hh_title = 'HeadHunter Moscow'
    sj_title = 'SuperJob Moscow'
    languages = ['CSS',
                 'JavaScript',
                 'Java',
                 'C#',
                 'Ruby',
                 'PHP',
                 'C++',
                 'Python']
    print(get_statistic_for_hh(languages, hh_title))
    print(get_statistic_for_sj(languages, sj_title, sj_token))
