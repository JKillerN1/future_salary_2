import os
import requests

from dotenv import load_dotenv
from itertools import count
from terminaltables import SingleTable


def create_table(language, vacancies_by_languages_hh, TABLE_DATA):
    TABLE_DATA.append([language, vacancies_by_languages_hh[language]['vacancies_found'],
                       vacancies_by_languages_hh[language]['vacancies_processed'],
                       vacancies_by_languages_hh[language]['average_salary']])
    return TABLE_DATA

def predict_rub_salary(vacancy_from, vacancy_to):
    if vacancy_from is None:
        return int(vacancy_to * 0.8)
    if vacancy_to is None:
        return int(vacancy_from * 1.2)
    return int((vacancy_from + vacancy_to) / 2)


def create_a_table_for_head_hunter(creat_table_hh):
    title_hh = 'HeadHunter Moscow'
    table_instance_hh = SingleTable(creat_table_hh, title_hh)
    return table_instance_hh.table


def get_statistic_for_hh(languages):
    lang={}
    vacancies_by_languages_hh = {}
    TABLE_DATA_hh = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]
    for language in languages:
        lang[language] = get_statistic_of_lang_hh(language, vacancies_by_languages_hh)
        TABLE_DATA_hh = create_table(language, lang, TABLE_DATA_hh)
    return create_a_table_for_head_hunter(TABLE_DATA_hh)


def get_statistic_of_lang_hh(language, vacancies_by_languages_hh):
    url_hh = 'https://api.hh.ru/vacancies'
    number_of_professions = 0
    average_salary = 0
    param = {'specialization': '1.221', 'area': '1', 'text': language, 'per_page': 100}
    response = requests.get(url_hh, params=param)
    response.raise_for_status()
    proggramer_vacancies_by_language = response.json()
    for page in range(proggramer_vacancies_by_language['pages']):
        param['page'] = page
        page_response = requests.get(url_hh, params=param)
        page_response.raise_for_status()
        vacancies_by_page = page_response.json()
        for vacancy in vacancies_by_page['items']:
            salary_vacancy = vacancy['salary']
            if salary_vacancy:
                if salary_vacancy['currency'] != 'RUR':
                    continue
                average_salary += predict_rub_salary(salary_vacancy['from'], salary_vacancy['to'])
                number_of_professions += 1
    vacancies_by_languages_hh[language] = {
        'vacancies_found': proggramer_vacancies_by_language['found'],
        'average_salary': average_salary // number_of_professions,
        'vacancies_processed': number_of_professions}
    return vacancies_by_languages_hh[language]


def create_a_table_for_superJob(create_table_sj):
    title_sj = 'SuperJob Moscow'
    table_instance_sj = SingleTable(create_table_sj, title_sj)
    return table_instance_sj.table


def get_statistic_for_sj(languages):
    lang_sj={}
    vacancies_by_languages_sj = {}
    TABLE_DATA_sj = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]
    for language in languages:
        lang_sj[language] = get_statistic_of_lang_sj(language, vacancies_by_languages_sj)
        TABLE_DATA_sj = create_table(language, lang_sj, TABLE_DATA_sj)
    return create_a_table_for_superJob(TABLE_DATA_sj)



def get_statistic_of_lang_sj(language, vacancies_by_languages_sj):
    load_dotenv()
    api_token = os.getenv('API_TOKEN')
    headers = {'X-Api-App-Id': api_token}
    sj_url = 'https://api.superjob.ru/2.0/vacancies'
    professions_sj_number = 0
    curuncy = 0
    sj_param = {'catalogues': 48, 'town': 4, 'keyword': language, 'count': 20, 'page': 0}
    iter_count = count(start=0, step=10)
    for number in iter_count:
        response = requests.get(sj_url, headers=headers, params=sj_param)
        response.raise_for_status()
        super_job = response.json()
        for vacancy in super_job['objects']:
           if vacancy['currency'] == 'rub' and vacancy['payment_from'] or vacancy['payment_to']:
                curuncy += predict_rub_salary(vacancy['payment_from'], vacancy['payment_to'])
                professions_sj_number += 1
        if super_job['more'] is False:
            break
        sj_param['page'] += 1
    vacancies_by_languages_sj[language] = {
        'vacancies_found': super_job['total'],
        'average_salary': curuncy // professions_sj_number,
        'vacancies_processed': professions_sj_number}

    return vacancies_by_languages_sj[language]


if __name__ == '__main__':
    languages = ['CSS', 'JavaScript', 'Java', 'C#', 'Ruby', 'PHP', 'C++', 'Python']
    print(get_statistic_for_hh(languages))
    print(get_statistic_for_sj(languages))
