import pytest
import covid_data_handler as c_data
import covid_news_handling as c_news
from utils import UpdateScheduler
from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates

import xmltodict
import logging

# Logger initialization
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('ProjectLogFile.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# PROVIDED TESTS


def test_parse_csv_data():
    data = c_data.parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639


def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()


def test_update_news():
    update_news('test')


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = \
        process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)


def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')


# PROJECT TESTS
# 15 rows (including headers)
data_to_test_summation = \
    [
        ["areaCode", "areaName", "areaType", "date",
         "cumDailyNsoDeathsByDeathDate", "hospitalCases",
         "newCasesBySpecimenDate"],
        ["E92000001", "England", "nation", "2021-09-30", "140372", "4916",
         "26243"],
        ["E92000001", "England", "nation", "2021-09-29", "140281", "5017",
         "28138"],
        ["E92000001", "England", "nation", "2021-09-28", "140194", '5126',
         "29016"],
        ["E92000001", "England", "nation", "2021-09-27", "140115", "5121",
         "33896"],
        ["E92000001", "England", "nation", "2021-09-26", "140037", "4949",
         "26265"],
        ["E92000001", "England", "nation", "2021-09-25", "139963", "5100",
         "22655"],
        ["E92000001", "England", "nation", "2021-09-24", "139875", "5036",
         "25213"],
        ["E92000001", "England", "nation", "2021-09-23", "139781", "5214",
         "27712"],
        ["E92000001", "England", "nation", "2021-09-22", "139678", "5406",
         "28185"],
        ["E92000001", "England", "nation", "2021-09-21", "139569", "5543",
         "29951"],
        ["E92000001", "England", "nation", "2021-09-20", "139475", "5727",
         "31453"],
        ["E92000001", "England", "nation", "2021-09-19", "139364", "5695",
         "24263"],
        ["E92000001", "England", "nation", "2021-09-18", "139267", "5688",
         "20524"],
        ["E92000001", "England", "nation", "2021-09-17", "139168", "5910",
         "21913"]
    ]

data_to_test_mrdp = \
    [
        ["areaCode", "areaName", "areaType", "date",
         "cumDailyNsoDeathsByDeathDate", "hospitalCases",
         "newCasesBySpecimenDate"],
        ["E92000001", "England", "nation", "2021-09-30", "", "", ""],
        ["E92000001", "England", "nation", "2021-09-29", "", "", ""],
        ["E92000001", "England", "nation", "2021-09-28", "", '5126', ""],
        ["E92000001", "England", "nation", "2021-09-27", "", "5121", ""],
        ["E92000001", "England", "nation", "2021-09-26", "140037", "4949", ""],
        ["E92000001", "England", "nation", "2021-09-25", "139963", "5100",
         "22655"],
        ["E92000001", "England", "nation", "2021-09-24", "139875", "5036",
         "25213"],
        ["E92000001", "England", "nation", "2021-09-23", "139781", "5214",
         "27712"],
        ["E92000001", "England", "nation", "2021-09-22", "139678", "5406",
         "28185"],
        ["E92000001", "England", "nation", "2021-09-21", "139569", "5543",
         "29951"],
        ["E92000001", "England", "nation", "2021-09-20", "139475", "5727",
         "31453"],
        ["E92000001", "England", "nation", "2021-09-19", "139364", "5695",
         "24263"],
        ["E92000001", "England", "nation", "2021-09-18", "139267", "5688",
         "20524"],
        ["E92000001", "England", "nation", "2021-09-17", "139168", "5910",
         "21913"]
    ]


@pytest.mark.parametrize("column_name, expected_value",
                         [
                             ("cumDailyNsoDeathsByDeathDate", 1957139),
                             ("hospitalCases", 74448),
                             ("newCasesBySpecimenDate", 375427)
                         ])
def test_finding_summation_over_rows(column_name, expected_value):
    """
    Tests finding_summation_over_rows function
    :param column_name: Parameter to pass into finding_summation_over_rows
    :param expected_value: Value to check function output against.
    """
    assert c_data.finding_summation_over_rows(
        data_to_test_summation, column_name, 14) == expected_value
    return None


@pytest.mark.parametrize("column_name, expected_value",
                         [
                             ("cumDailyNsoDeathsByDeathDate", 140037),
                             ("hospitalCases", 5126),
                             ("newCasesBySpecimenDate", 22655)
                         ])
def test_finding_most_recent_datapoint(column_name, expected_value):
    """
    Tests finding_most_recent_datapoint function
    :param column_name: Parameter to pass into finding_summation_over_rows
    :param expected_value: Value to check function output against.
    """
    assert c_data.finding_most_recent_datapoint(
        data_to_test_mrdp, column_name) == expected_value


def test_process_covid_csv_data_mine():
    """
    Tests process_covid_csv_data function output against expected values.
    """
    last7days_cases, current_hospital_cases, total_deaths = \
        c_data.process_covid_csv_data(c_data.parse_csv_data
                                      ('nation_2021-10-28.csv'))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_covid_API_request_necessary_data():
    """
    Tests if covid_API_request returns the necessary data if data necessary
    for the functioning of the dashboard isn't in config.
    """
    # Update c_data.config to see if necessary data is forced in.
    config_copy = c_data.config
    # Stripping the data necessary for the dashboard to function
    c_data.config["structure"] = {'areaCode': 'areaCode',
                                  'areaName': 'areaName',
                                  'areaType': 'areaType',
                                  'date': 'date'}
    data = c_data.covid_API_request()
    # The following assertions indicate that the data essential to the
    # dashboard's functioning was still accessed and processed despite
    # its absence from the structure
    assert data["L7DIR"] >= 0
    assert data["N7DIR"] >= 0
    assert data["CHCases"] >= 0
    assert data["TD"] >= 0
    c_data.config = config_copy


def test_covid_API_request_additional_data():
    """
    Tests if additional data is returned by the covid_API_request when config
    has values to be processed in the summation_area, summation_data,
    most_recent_datapoint_country and most_recent_datapoint_area fields.
    """
    # Update c_data.config to add data.
    config_copy = c_data.config
    # Stripping the data necessary for the dashboard to function
    c_data.config["structure"].update({"VaccinatedPeople":
                                "cumPeopleVaccinatedCompleteByPublishDate"})
    # item = (name_of_column_csv, user_defined_dict_key,
    # number_of_days, skip)
    c_data.config["summation_area"] = \
        [("VaccinatedPeople", "VaxxSumArea", 7, 0)]
    c_data.config["summation_country"] = \
        [("VaccinatedPeople", "VaxxSumCountry", 7, 0)]
    c_data.config["most_recent_datapoint_area"] = \
        [("VaccinatedPeople", "VaxxMRDPArea", 0)]
    c_data.config["most_recent_datapoint_country"] = \
        [("VaccinatedPeople", "VaxxMRDPCountry", 0)]
    data = c_data.covid_API_request()
    assert data['VaxxSumArea']
    assert data['VaxxSumCountry']
    assert data['VaxxMRDPArea']
    assert data['VaxxMRDPCountry']
    # The following assertions indicate that the data essential to the
    # dashboard's functioning was still accessed and processed despite
    # its absence from the structure
    c_data.config = config_copy


def test_update_stats():
    """
    Tests update_stats function by making stats an empty dictionary and then
    running the update_stats function and ensuring it is not empty after.
    """
    stats_copy = c_data.stats
    c_data.stats = {}
    c_data.update_stats()
    assert c_data.stats != {}
    c_data.stats = stats_copy


def test_update_stats_repeat():
    """
    Tests update_stats_repeat function by making stats an empty dictionary and
    then running the update_stats function and ensuring it is not empty after.
    It also checks the length of the UpdateScheduler's queue before and after
    the function is called to ensure update_stats_repeat schedules itself.
    """
    stats_copy = c_data.stats
    c_data.stats = {}
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_data.update_stats("tester", 60)
    assert c_data.stats != {}
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_data.stats = stats_copy
    c_data.cancel_scheduled_stats_updates("tester")


def test_schedule_covid_updates_mine():
    """
    Tests schedule_covid_updates function by scheduling an update checks the
    length of the UpdateScheduler's queue before and after the function is
    called to ensure the function works as intended.
    """
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_data.schedule_covid_updates(update_interval=10, update_name='update test')
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_data.cancel_scheduled_stats_updates("update test")


def test_schedule_repeating_covid_updates():
    """
    Tests schedule_covid_updates function ability to schedule repeating updates
    by scheduling an update  checks  he length of the UpdateScheduler's queue
    before and after the function is called to ensure the function works as
    intended.
    """
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_data.schedule_covid_updates(update_interval=10, update_name='update test',
                                  repeating=True)
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_data.cancel_scheduled_stats_updates("update test")


def test_cancel_scheduled_stats_updates():
    """
    Tests cancel_scheduled_stats_updates function ability to cancel scheduling
    updates by creating update and cancelling it.
    """
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_data.schedule_covid_updates(update_interval=10,
                                  update_name='cancel update test',
                                  repeating=True)
    c_data.cancel_scheduled_stats_updates("cancel update test")
    assert len(UpdateScheduler.queue) == scheduled_updates_before


def test_news_API_request_mine():
    """Testing the news API request"""
    assert c_news.news_API_request()
    assert c_news.news_API_request('Covid COVID-19 coronavirus') == \
           c_news.news_API_request()


def test_news_API_request_relevance():
    """Testing if the News API returns relevant news articles."""
    assert c_news.news_API_request() != c_news.news_API_request("Computer")


def test_update_news_mine():
    """
    Tests update_news function by making news_articles an empty list and
    then running the update_news function and ensuring it is not empty after.
    """
    news_copy = c_news.news_articles
    c_news.news_articles = []
    c_news.update_news()
    assert c_news.news_articles != []
    c_news.news = news_copy


def test_update_news_repeat():
    """
    Tests update_news function with the repeat_interval by making news_articles
    an empty list and then running the update_news function and ensuring it is
    not empty after. It also checks the length of the UpdateScheduler's queue
    before and after the function is called to ensure update_news schedules
    itself.
    """
    news_copy = c_news.news_articles
    c_news.news_articles = []
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_news.update_news("tester", "test", 60)
    assert c_news.news_articles != []
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_news.news_articles = news_copy
    c_news.cancel_scheduled_news_updates("tester")


def test_schedule_news_updates():
    """
    Tests schedule_news_updates function by scheduling an update checks the
    length of the UpdateScheduler's queue before and after the function is
    called to ensure the function works as intended.
    """
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_news.schedule_news_updates(update_interval=10, update_name='update test')
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_news.cancel_scheduled_news_updates("update test")


def test_schedule_repeating_news_updates():
    """
    Tests schedule_news_updates function by scheduling a repeating update and
    then checks the length of the UpdateScheduler's queue before and after the
    function is called to ensure the function works as intended.
    """
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_news.schedule_news_updates(update_interval=10, update_name='update test',
                                 repeating=True)
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_news.cancel_scheduled_news_updates("update test")


def test_remove_article():
    """
    Tests that the necessary article is removed from the news_articles list.
    """
    news_copy = c_news.news_articles
    c_news.news_articles = []
    c_news.update_news()
    length_before_remove = len(c_news.news_articles)
    c_news.remove_article(c_news.news_articles[0]["title"])
    assert len(c_news.news_articles) < length_before_remove
    c_news.news = news_copy


def run_all_tests():
    """
    Runs all tests creates an xml file with the test results.
    Reads xml file and logs any  failures.
    """
    pytest.main(["--junitxml=TestResults.xml", 'testing.py'])
    with open('TestResults.xml') as file:
        doc = xmltodict.parse(file.read())
    if int(doc['testsuites']['testsuite']['@failures']) >= 1:
        for test in (doc['testsuites']['testsuite']['testcase']):
            if 'failure' in test.keys():
                logger.error(test['@name'] + ' failed')
    else:
        logger.info('All tests passed.')

