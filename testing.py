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
    assert c_data.finding_most_recent_datapoint(
        data_to_test_mrdp, column_name) == expected_value


def test_process_covid_csv_data_mine():
    last7days_cases, current_hospital_cases, total_deaths = \
        c_data.process_covid_csv_data(c_data.parse_csv_data
                                      ('nation_2021-10-28.csv'))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_covid_API_request_necessary_data():
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
    # It is checked against an empty dictionary since it is not possible to know
    # when exactly the stats are updated and there is a very slight
    # possibility that they stay the same as the previous update leading to a
    # false error
    stats_copy = c_data.stats
    c_data.stats = {}
    c_data.update_stats()
    assert c_data.stats != {}
    c_data.stats = stats_copy


def test_update_stats_repeat():
    # It is checked against an empty dictionary since it is not possible to know
    # when exactly the stats are updated and there is a very slight
    # possibility that they stay the same as the previous update leading to a
    # false error. Also checks if an item is scheduled.
    stats_copy = c_data.stats
    c_data.stats = {}
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_data.update_stats_repeat("tester")
    assert c_data.stats != {}
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_data.stats = stats_copy
    c_data.cancel_scheduled_stats_updates("tester")


def test_schedule_covid_updates_mine():
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_data.schedule_covid_updates(update_interval=10, update_name='update test')
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_data.cancel_scheduled_stats_updates("update test")


def test_schedule_repeating_covid_updates():
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_data.schedule_covid_updates(update_interval=10, update_name='update test',
                                  repeating=True)
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_data.cancel_scheduled_stats_updates("update test")


def test_cancel_scheduled_stats_updates():
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_data.schedule_covid_updates(update_interval=10,
                                  update_name='cancel update test',
                                  repeating=True)
    c_data.cancel_scheduled_stats_updates("cancel update test")
    assert len(UpdateScheduler.queue) == scheduled_updates_before


def test_news_API_request_mine():
    assert c_news.news_API_request()
    assert c_news.news_API_request('Covid COVID-19 coronavirus') == \
           c_news.news_API_request()


def test_news_API_request_number_of_articles():
    config_copy = c_news.config
    c_news.config['number_of_articles_on_the_page'] = 5
    assert len(c_news.news_API_request()) == 5
    c_news.config = config_copy


def test_news_API_request_relevance():
    assert c_news.news_API_request() != c_news.news_API_request("Computer")


def test_update_news_mine():
    # It is checked against an empty list since it is not possible to know
    # when exactly the news is updated and there is a  very slight
    # possibility that they stay the same as the previous update leading to a
    # false error
    news_copy = c_news.news_articles
    c_news.news_articles = []
    c_news.update_news()
    assert c_news.news_articles != []
    c_news.news = news_copy


def test_update_news_repeat():
    # It is checked against an empty list since it is not possible to know
    # when exactly the news is updated and there is a  very slight
    # possibility that they stay the same as the previous update leading to a
    # false error. Also checks if an item is scheduled.
    news_copy = c_news.news_articles
    c_news.news_articles = []
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_news.update_news_repeat("tester")
    assert c_news.news_articles != []
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_news.news_articles = news_copy
    c_news.cancel_scheduled_news_updates("tester")


def test_schedule_news_updates():
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_news.schedule_news_updates(update_interval=10, update_name='update test')
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_news.cancel_scheduled_news_updates("update test")


def test_schedule_repeating_news_updates():
    scheduled_updates_before = len(UpdateScheduler.queue)
    c_news.schedule_news_updates(update_interval=10, update_name='update test',
                                  repeating=True)
    assert len(UpdateScheduler.queue) > scheduled_updates_before
    c_news.cancel_scheduled_news_updates("update test")


def test_remove_article():
    news_copy = c_news.news_articles
    c_news.news_articles = []
    c_news.update_news()
    length_before_remove = len(c_news.news_articles)
    c_news.remove_article(c_news.news_articles[0]["title"])
    print(len(c_news.news_articles))
    print(length_before_remove)
    assert len(c_news.news_articles) < length_before_remove
    c_news.news = news_copy
