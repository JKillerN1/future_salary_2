import requests
from terminaltables import SingleTable

languages = ['CSS', 'JavaScript', 'Java', 'C#', 'Ruby', 'PHP', 'C++', 'Python']


TABLE_DATA_hh = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]

TABLE_DATA_sj = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]

def table_hh(language, vacancies_by_languages_hh):
    TABLE_DATA_hh.append([language, vacancies_by_languages_hh[language]['vacancies_found'],
                       vacancies_by_languages_hh[language]['vacancies_processed'],
                       vacancies_by_languages_hh[language]['average_salary']])

    return TABLE_DATA_hh


def predict_rub_salary(vacancy):
    if vacancy['currency'] == 'RUR':
        if vacancy['from'] == None:
            return int(vacancy['to'] * 0.8)
        if vacancy['to'] == None:
            return int(vacancy['from'] * 1.2)
        return int((vacancy['from'] + vacancy['to']) / 2)


def head_hunter_table(languages):
    title_hh = 'HeadHunter Moscow'
    vacancies_by_languages_hh = {}
    url_hh = 'https://api.hh.ru/vacancies'

    for language in languages:
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
                    average_salary += predict_rub_salary(salary_vacancy)
                    number_of_professions += 1

            vacancies_by_languages_hh[language] = {'vacancies_found': proggramer_vacancies_by_language['found'],
                                                    'average_salary': average_salary // number_of_professions,
                                                    'vacancies_processed': number_of_professions}

        table_instance_hh = SingleTable(table_hh(language, vacancies_by_languages_hh), title_hh)

    return table_instance_hh.table





def table_sj(language, vacancies_by_languages_sj):
     TABLE_DATA_sj.append([language, vacancies_by_languages_sj[language]['vacancies_found'],
                        vacancies_by_languages_sj[language]['vacancies_processed'],
                        vacancies_by_languages_sj[language]['average_salary']])
     return TABLE_DATA_sj

def predict_rub_salary_for_superJob(vacancy):
    if vacancy['currency'] == 'rub':
        if vacancy['payment_from'] == 0:
            return int(vacancy['payment_to'] * 0.8)
        if vacancy['payment_to'] == 0:
            return int(vacancy['payment_from'] * 1.2)
        return int((vacancy['payment_from'] + vacancy['payment_to']) / 2)

def super_job_table(languages):
    title_sj = 'SuperJob Moscow'
    vacancies_by_languages_sj = {}

    api = 'v3.r.135730693.e747e6daf76ce7b6302f4626a8eda784e6fe643d.82b2c4895662b62a11311215463b69c30479818d'
    d = {'X-Api-App-Id': api}
    url_sj = 'https://api.superjob.ru/2.0/vacancies'

    for language in languages:
        number_of_professions_sj = 0
        curuncy = 0

        param_sj = {'catalogues': 48, 'town': 4, 'keyword': language, 'count': 20, 'page': 0}
        while True:
            response = requests.get(url_sj, headers=d, params=param_sj)
            response.raise_for_status()
            super_job = response.json()

            for i in super_job['objects']:
                if i['currency'] == 'rub' and i['payment_from'] != 0 or i['payment_to'] != 0:
                    curuncy += predict_rub_salary_for_superJob(i)
                    number_of_professions_sj += 1

                    vacancies_by_languages_sj[language] = {'vacancies_found': super_job['total'],
                                                        'average_salary': curuncy // number_of_professions_sj,
                                                        'vacancies_processed': number_of_professions_sj}

            if super_job['more'] == False:
                break

            param_sj['page'] += 1
        table_instance_sj = SingleTable(table_sj(language, vacancies_by_languages_sj), title_sj)

    return table_instance_sj.table



print(head_hunter_table(languages))
print()
print(super_job_table(languages))