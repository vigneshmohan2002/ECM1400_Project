from uk_covid19 import Cov19API
from miscellaneous import json_processor, UpdateScheduler

config = json_processor('config.json')

ud_location = config["ud_location"]
ud_location_type = config["ud_location_type"]

# Global variable that will be accessed here and in user_interface module
stats = {}

scheduled_stats_updates = {}


def parse_csv_data(csv_filename: str):
    """
    This function takes in a csv file and parses it to return a list of strings,
    each string comprises one line in the file.

    :param csv_filename: The filepath to the csv file containing the data.
    :return parsed_data: A list of strings containing values separated by commas
    """
    with open(csv_filename, 'r') as f:
        parsed_data = []
        for line in f:
            parsed_data.append(line)
    return parsed_data


def process_covid_csv_data(covid_csv_data: list):
    """
    This function takes in a list of lines as produced by the
    parse_csv_data function and returns statistics on the data from the
    .csv file.

    :param covid_csv_data: A list of strings containing values separated by
    commas
    :return last7days_cases: Total cases over the last 7 days
    :return current_hospital_cases: Current COVID-19 cases in the hospital
    :return total_deaths: Total deaths from COVID-19
    """
    # Splitting the strings to generate a list of values from each
    processed_data = table_generator(covid_csv_data)

    # Removing the new line "/n" from the last element
    processed_data[0][-1] = processed_data[0][-1][:-1]

    # Get the string args from config.json instead of using literals.

    # Getting hospital cases
    if 'hospitalCases' in config['structure'].values():
        key = get_key('hospitalCases', config['structure'])
        current_hospital_cases = finding_most_recent_datapoint(processed_data,
                                                               key)
    else:
        current_hospital_cases = finding_most_recent_datapoint(processed_data,
                                                               "hospCases")

    # Getting cases over last 7 days.
    if 'newCasesBySpecimenDate' in config['structure'].values():
        key = get_key('newCasesBySpecimenDate', config['structure'])
        last7days_cases = finding_summation_over_rows(processed_data,
                                                      key, 7, 1)
    else:
        last7days_cases = finding_summation_over_rows(processed_data,
                                                  "newCases", 7, 1)

    # Finding total deaths
    if 'cumDailyNsoDeathsByDeathDate' in config['structure'].values():
        key = get_key('cumDailyNsoDeathsByDeathDate', config['structure'])
        total_deaths = finding_most_recent_datapoint(processed_data,
                                                               key)
    else:
        total_deaths = finding_most_recent_datapoint(processed_data,
                                                 "cumDailyDeaths")

    return last7days_cases, current_hospital_cases, total_deaths


def get_key(v, kvdict):
    """
    This function finds the key from a key-pair value in a dictionary from the
    value.

    :param v: A value in the dictionary
    :param kvdict: A key-value dictionary
    :return key: The key to which they value in the dictionary is paired
    """
    for key, value in kvdict.items():
        if v == value:
            return key
    return None


def table_generator(data):
    """
    This function generates a lis of lists of values from a list of strings.

    :param data: A list of strings containing values separated by commas.
    :return processed_data: A list of lists containing values.
    """
    processed_data = []
    for line in data:
        processed_data.append(line.split(','))
    return processed_data


def finding_most_recent_datapoint(data: list, column_index: str, skip: int = 0):
    """
    This function finds the most recent datapoint from a table skipping rows as
    needed from a specified column.

    :param data: A list of lists containing values.
    :param column_index: The name of the column where the data to be processed
    is stored.
    :param skip: The number of rows to be skipped as needed (usually in the case
    of incomplete values)
    :return mrdp: The most recent datapoint
    """
    if type(column_index) == str:
        column_index = data[0].index(column_index)
    mrdp = 0  # mrdp is most recent datapoint
    if skip <= 0:
        try:
            for line in data[1:]:
                if line[column_index].isnumeric():
                    mrdp = int(line[column_index])
                    break
        except IndexError:
            return 0
    else:  # Executed if skip is specified as a positive value.
        try:
            for line in data[1:]:
                if line[column_index].isnumeric():
                    skip -= 1
                    if skip < 0:
                        mrdp = int(line[column_index])
                    break
        except IndexError:
            return 0
    return mrdp


def finding_summation_over_rows(data: list, column_index: str,
                        number_of_days: int, skip: int = 0):
    """
    This function finds the sum of the values over a specified number of rows in
    a specified column from a table skipping rows as needed from a specified
    column.

    :param data: A list of lists containing values.
    :param column_index: The name of the column where the data to be processed
    is stored.
    :param number_of_days: The number of days or rows of data to be summed up.
    :param skip: The number of rows to be skipped as needed (usually in the case
    of incomplete values)
    :return summation_over_rows: The summation over rows.
    """
    if type(column_index) == str:
        column_index = data[0].index(column_index)
    summation_over_rows = 0
    starting_row = 0

    # Loop to find the index of first filled datapoint in the column
    for line in data[1:]:
        starting_row += 1
        if starting_row > (len(data) - 2):
            break
        if line[column_index].strip().isnumeric():
            break

    # Skipping data-points containing incomplete data if applicable
    if skip > 0:
        starting_row += skip

    # Summing the necessary data-points.
    if starting_row > 1:
        ending_row = starting_row + (number_of_days - 1)
        while starting_row <= ending_row:
            try:
                summation_over_rows += int(data[starting_row]
                                       [column_index])
            except IndexError:
                # Leaves the sum of days where data was available instead of
                # returning 0 (Consider returning string showing lack of data?)
                break
            starting_row += 1
    return summation_over_rows


def covid_API_request(location="Exeter", location_type="ltla"):
    """
    This function is used to access the UK COVID-19 API to pull data for the
    necessary location and return the requested statistics.

    :param location: The location for which data is required
    :param location_type: The type of location
    :return covid_data: A dictionary containing statistical values with its
    title as the keys.
    """
    area_filter = ['areaType=' + location_type, 'areaName=' + location]
    country_filter = ['areaType=nation', 'areaName=England']

    # config.json is used to pull the file structure.

    csv_file_structure = config['structure']

    # cumDailyNsoDeathsByDeathDate, hospitalCases, newCasesBySpecimenDate is
    # necessary for the dashboard to function. Therefore it is checked
    # whether it is included in the file structure and updated if it is not.

    necessary_data = {'cumDailyDeaths': 'cumDailyNsoDeathsByDeathDate',
                      'hospCases': 'hospitalCases',
                      'newCases': 'newCasesBySpecimenDate'}

    for item in necessary_data.values():
        if not (item in csv_file_structure.values()):
            csv_file_structure.update(item)

    area_api = Cov19API(filters=area_filter, structure=csv_file_structure)
    country_api = Cov19API(filters=country_filter, structure=csv_file_structure)

    # Extracting data for the local area.
    area_api.get_csv(save_as="area_data.csv")

    # Storing the parsed data in a variable allows it to use it again later
    # This prevents unnecessarily running the function twice
    area_data = parse_csv_data("csv_data/area_data.csv")

    area_7dir, area_chc, area_td = \
        process_covid_csv_data(area_data)

    # Extracting data for the country
    country_api.get_csv(save_as="country_data.csv")

    # Storing the parsed data in a variable allows it to use it again later.
    # This prevents unnecessarily running the function twice.
    country_data = parse_csv_data("csv_data/country_data.csv")

    country_7dir, country_chc, country_td = \
        process_covid_csv_data(country_data)

    # Creating a dictionary.
    # Adding to the dictionary using the generalized functions on the data
    # is a possibility. We'd simply need to call the function and pass in the
    # area_data or country_data as necessary and run it through table_generator
    # and then give in the needed column names.
    covid_data = {"L7DIR": area_7dir,
                  "N7DIR": country_7dir,
                  "CHCases": country_chc,
                  "TD": country_td
                  }
    additional_data = {}

    # Processing additional data for area

    if len(config['summation_area']) > 0 or \
            len(config['most_recent_datapoint_area']) > 0:
        processed_area_data = table_generator(area_data)
        if len(config['summation_area']) > 0:
            for item in config['summation_area']:
                try:
                    updater = {item[1]: finding_summation_over_rows(
                        processed_area_data, item[0], item[2], item[3])}
                except ValueError:
                    updater = {item[1]: "Not in CSV file, update the structure"}
                except:
                    updater = {item[1]: "Error"}
                additional_data.update(updater)

        if len(config['most_recent_datapoint_area']) > 0:
            for item in config['most_recent_datapoint_area']:
                try:
                    updater = {item[1]: finding_most_recent_datapoint(
                        processed_area_data, item[0], item[2])}
                except ValueError:
                    updater = {item[1]: "Not in CSV file, update the structure"}
                except:
                    updater = {item[1]: "Error"}
                additional_data.update(updater)

    # Processing additional data for country

    if len(config['summation_country']) > 0 or \
            len(config['most_recent_datapoint_country']) > 0:
        processed_country_data = table_generator(area_data)
        if len(config['summation_country']) > 0:
            for item in config['summation_country']:
                try:
                    updater = {item[1]: finding_summation_over_rows(
                        processed_country_data, item[0], item[2], item[3])}
                except ValueError:
                    updater = {item[1]: "Not in CSV file, update the structure"}
                except:
                    updater = {item[1]: "Error"}
                additional_data.update(updater)

        if len(config['most_recent_datapoint_country']) > 0:
            for item in config['most_recent_datapoint_country']:
                try:
                    updater = {item[1]: finding_most_recent_datapoint(
                        processed_country_data, item[0], item[2])}
                except ValueError:
                    updater = {item[1]: "Not in CSV file, update the structure"}
                except:
                    updater = {item[1]: "Error"}
                additional_data.update(updater)

    covid_data.update(additional_data)
    return covid_data


def update_stats():
    """
    This function updates the global stats variable that is accessed by the
    user_interface module when scheduled.
    """
    global ud_location
    global ud_location_type
    global stats
    if ud_location == "":
        stats = covid_API_request()
    else:
        stats = covid_API_request(ud_location,
                                 ud_location_type)
    return None


def update_stats_repeating(update_name):
    """
    This function updates the global stats variable that is accessed by the
    user_interface module when scheduled. It also schedules itself to run again
    in 24 hours under the same update name so that it may be canceled if
    requested by the user.

    :param update_name: The name of the update
    """
    global ud_location
    global ud_location_type
    global stats
    if ud_location == "":
        stats = covid_API_request()
        task = UpdateScheduler.enter(24*60*60, 1, update_stats_repeating,
                                     argument=update_name)
        scheduled_stats_updates.update({update_name: task})
    else:
        stats = covid_API_request(ud_location, ud_location_type)
        task = UpdateScheduler.enter(24*60*60, 1, update_stats_repeating,
                                     argument=update_name)
        scheduled_stats_updates.update({update_name: task})
    return None


def schedule_covid_updates(update_name: str, update_interval: int):
    """
    This function schedules updates to the stats variable using the
    scheduler.enter() function from the sched module and the update_stats
    function.
    :param update_name: The name of the update
    :param update_interval: The interval to pass into the scheduler.enter
    function
    """
    scheduled_stats_updates.update({update_name: UpdateScheduler.enter
    (update_interval, 1, update_stats)})


def schedule_repeating_covid_updates(update_name: str, update_interval: int):
    """
    This function schedules repeating updates to the stats variable using the
    scheduler.enter() function from the sched module and the
    update_stats_repeating function.

    :param update_name: The name of the update
    :param update_interval: The interval to pass into the scheduler.enter
    function
    """
    scheduled_stats_updates.update({update_name: UpdateScheduler.enter
    (update_interval, 1, update_stats_repeating, argument=update_name)})


def cancel_scheduled_stats_updates(update_name: str):
    """
    This function cancels scheduled updates to the stats variable using the
    scheduler.cancel() function from the sched module and accessing the global
    scheduled_stats_updates dictionary.

    :param update_name: The name of the update
    """
    try:
        UpdateScheduler.cancel(scheduled_stats_updates[update_name])
        del scheduled_stats_updates[update_name]
    except KeyError:
        pass
    return None
