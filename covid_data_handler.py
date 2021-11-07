from uk_covid19 import Cov19API
import sched


def parse_csv_data(csv_filename):
    with open(csv_filename, 'r') as f:
        parsed_data = []
        for line in f:
            parsed_data.append(line)
    return parsed_data


def process_covid_csv_data(covid_csv_data):
    processed_data = []
    total_deaths = 0
    for line in covid_csv_data:
        processed_data.append(line.split(','))
    current_hospital_cases = processed_data[1][5]
    print(current_hospital_cases)
    last7days_cases = 0
    i = 3
    while i <= 9:
        last7days_cases += int(processed_data[i][6])
        i += 1
    for line in processed_data:
        if line[4] == '' or line[4] == 'cumDailyNsoDeathsByDeathDate':
            continue
        else:
            total_deaths = line[4]
            break
    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(location="Exeter", location_type="ltla"):
    area_filter = ['areaType=' + location_type, 'areaName=' + location]
    csv_file_structure = \
        {
            "areaCode": "areaCode",
            "areaName": "areaName",
            "areaType": "areaType",
            "date": "date",
            "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
            "hospitalCases": "hospitalCases",
            "newCasesBySpecimenDate": "newCasesBySpecimenDate",
        }
    api = Cov19API(filters=area_filter, structure=csv_file_structure)
    d1, d2, d3 = process_covid_csv_data(parse_csv_data(api.get_csv()))
    covid_data = {"7 day infection rate": d1,
                  "Current hospital cases": d2,
                  "Total deaths": d3}
    return covid_data


def schedule_covid_updates(update_interval, update_name):
    # Leave aside for today.
    return None
