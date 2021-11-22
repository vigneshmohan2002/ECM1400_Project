from uk_covid19 import Cov19API
import sched


def parse_csv_data(csv_filename):
    """
    This function takes in the filename as a parameter so it may locate the
    corresponding csv file and parses it to return a list of all the lines
    in the file.
    """
    with open(csv_filename, 'r') as f:
        parsed_data = []
        for line in f:
            parsed_data.append(line)
    return parsed_data


def process_covid_csv_data(covid_csv_data):
    """
    This function takes in the list of all the lines as produced by the
    parse_csv_data function as a parameter so it may process it to return
    last7days_cases, current_hospital_cases, total_deaths.
    """
    processed_data = []
    total_deaths = 0
    for line in covid_csv_data:
        processed_data.append(line.split(','))

    # Removing the new line "/n" from the last element
    processed_data[0][-1] = processed_data[0][-1][:-1]

    # Retrieving the index of headers from processed_data[0]
    index_death = processed_data[0].index("cumDailyDeaths")
    index_hosp = processed_data[0].index("hospCases")
    index_infection = processed_data[0].index("newCases")

    # Getting hospital cases
    current_hospital_cases = 0
    try:
        for line in processed_data[1:]:
            if line[index_hosp].isnumeric():
                current_hospital_cases = int(line[index_hosp])
                break
    except IndexError:
        current_hospital_cases = 0

    # Want to prevent usage of literals.
    last7days_cases = 0
    starting_row = 0
    # Finding cases in the last 7 days
    # Loop to find the index of first filled datapoint in the column
    for line in processed_data[1:]:
        starting_row += 1
        if starting_row > (len(processed_data) - 2):
            break
        if line[index_infection].strip().isnumeric():
            break
    starting_row += 1  # To skip the datapoint containing incomplete data
    if starting_row > 1:
        ending_row = starting_row + 6
        while starting_row <= ending_row:
            try:
                last7days_cases += int(processed_data[starting_row]
                                       [index_infection])
            except IndexError:
                # Leaves the sum of days where data was available instead of
                # giving no data
                break
            starting_row += 1
    else:
        last7days_cases = 0

    # Finding total deaths
    try:
        for line in processed_data[1:]:
            if line[index_death].isnumeric():
                total_deaths = int(line[index_death])
                break
    except IndexError:
        total_deaths = 0
    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(location="Exeter", location_type="ltla"):
    area_filter = ['areaType=' + location_type, 'areaName=' + location]
    country_filter = ['areaType=nation', 'areaName=England']
    csv_file_structure = \
        {
            "areaCode": "areaCode",
            "areaName": "areaName",
            "areaType": "areaType",
            "date": "date",
            "cumDailyDeaths": "cumDailyNsoDeathsByDeathDate",
            "hospCases": "hospitalCases",
            "newCases": "newCasesBySpecimenDate",
        }
    area_api = Cov19API(filters=area_filter, structure=csv_file_structure)
    country_api = Cov19API(filters=country_filter, structure=csv_file_structure)

    # Extracting data for the local area.
    area_api.get_csv(save_as="area_data.csv")
    area_7dir, area_chc, area_td = \
        process_covid_csv_data(parse_csv_data("area_data.csv"))

    # Extracting data for the country
    country_api.get_csv(save_as="country_data.csv")
    country_7dir, country_chc, country_td = \
        process_covid_csv_data(parse_csv_data("country_data.csv"))

    # Creating a dictionary.
    covid_data = {"L7DIR": area_7dir,
                  "N7DIR": country_7dir,
                  "CHCases": country_chc,
                  "TD": country_td
                  }
    return covid_data


# One function to schedule NON-repeating updates
# Another to schedule repeating updates? Use an if statement in the user
# interface part to decide which function to call?
# use update_name to give info to the function? NU = news update,
# SU = stats update, NSU = news and stats update (small string makes more
# efficient)


def schedule_covid_updates(update_interval, update_name):
    # Leave aside.
    return None
