from flask import Flask
from flask import render_template
from flask import request
from flask import redirect as rd, url_for
import covid_data_handler as c_data
import covid_news_handling as c_news
from utils import json_processor, UpdateScheduler, required_interval as interval
from utils import TestScheduler
import logging
import testing

config = json_processor('config.json')  # Global variable since used throughout

app = Flask(__name__)

ud_location = config['ud_location']

if ud_location == "":
    ud_location = "Exeter"

# Logger initialization
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('ProjectLogFile.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

ud_location_type = config['ud_location_type']

c_data.update_stats()
c_news.update_news(config['ud_search_terms'])

ui_scheduled_updates = []


def continuous_testing():
    """
    Schedules tests to be run every 24 hours and runs the scheduler,
    :return:
    """
    TestScheduler.enter(24*60*60, 1, testing.run_all_tests)
    TestScheduler.run(blocking=False)


def removing_finished_updates(finished_update: str) -> None:
    """
    This function ensures that updates are removed from all records in which
    they may be present. There are 3 records one for user_interface,
    covid_news_handling, and covid_data handler.
    :param finished_update: Name of the finished update.
    """
    for update in ui_scheduled_updates:
        if update['title'] == finished_update:
            ui_scheduled_updates.remove(update)
    if "(News)" in finished_update:
        del c_news.scheduled_news_updates[finished_update]
    elif "(Statistics)" in finished_update:
        del c_data.scheduled_stats_updates[finished_update]
    else:
        del c_news.scheduled_news_updates[finished_update]
        del c_data.scheduled_stats_updates[finished_update]
    return None


@app.route('/')
def redirect():
    """
    Simply redirects the user to /index. No other purpose.
    :return: redirects the web app to /index.
    """
    return rd(url_for('button_responses'))


@app.route('/index')
def button_responses() -> object:
    """
    This function is responsible for running the web application. When any
    button is triggered, the arguments are received here and the necessary
    actions are taken.
    :return: An html file generated using the render_template function from the
    flask module.
    """
    # Receiving any arguments that are sent when the submit button is triggered.
    update_name = request.args.get('two')  # Textbox for update name
    update_time = request.args.get('update')  # Textbox for update time.
    repeat = request.args.get('repeat')  # Checkbox for repeating or not
    covid_ud = request.args.get('covid-data')  # Checkbox for covid updates
    news_ud = request.args.get('news')  # Checkbox for  news updates
    # This will be run if the Submit button is triggered.
    if update_name:
        if update_time:
            # Each if statement here corresponds to whether both the news and
            # stats update checkboxes were triggered or if either one was
            # triggered.
            if covid_ud and news_ud:  # Stats and News checkboxes are triggered
                if repeat:
                    update_name = update_name + ' (News and statistics)' + \
                                  '(Repeating)'
                    logger.info('User tries to schedule update: %s for %s',
                                update_name, update_time)
                    c_data.schedule_covid_updates(update_name,
                                                  update_time=update_time,
                                                  repeating=True)
                    c_news.schedule_news_updates(update_name,
                                                 update_time=update_time,
                                                 repeating=True)
                    # Adding to the user_interface updates record.
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                else:
                    update_name = update_name + ' (News and statistics)'
                    logger.info('User tries to schedule update: %s for %s',
                                update_name, update_time)
                    c_data.schedule_covid_updates(update_name,
                                                  update_time=update_time)
                    c_news.schedule_news_updates(update_name,
                                                 update_time=update_time)
                    # Adding to the user_interface updates record.
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                    # Scheduling the removal after it's performed
                    UpdateScheduler.enter(interval(update_time), 3,
                                          removing_finished_updates,
                                         argument=(update_name,))
            elif covid_ud:  # Stats checkbox is triggered
                if repeat:
                    update_name = update_name + ' (Statistics)(Repeating)'
                    logger.info('User tries to schedule update: %s for %s',
                                update_name, update_time)
                    c_data.schedule_covid_updates(update_name,
                                                  update_time=update_time,
                                                  repeating=True)
                    # Adding to the user_interface updates record.
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                else:
                    update_name = update_name + ' (Statistics)'
                    logger.info('User tries to schedule update: %s for %s',
                                update_name, update_time)
                    c_data.schedule_covid_updates(update_name,
                                                  update_time=update_time)
                    # Adding to the user_interface updates record.
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                    # Scheduling the removal after it's performed
                    UpdateScheduler.enter(interval(update_time), 3,
                                          removing_finished_updates,
                                         argument=(update_name,))
            elif news_ud:  # News checkbox is triggered
                if repeat:
                    update_name = update_name + ' (News)(Repeating)'
                    logger.info('User tries to schedule update: %s for %s',
                                update_name, update_time)
                    c_news.schedule_news_updates(update_name,
                                                 update_time=update_time,
                                                 repeating=True)
                    # Adding to the user_interface updates record.
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                else:
                    update_name = update_name + ' (News)'
                    logger.info('User tries to schedule update: %s for %s',
                                update_name, update_time)
                    c_news.schedule_news_updates(update_name,
                                                 update_time=update_time)
                    # Adding to the user_interface updates record.
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                    # Scheduling the removal after it's performed
                    UpdateScheduler.enter(interval(update_time), 3,
                                          removing_finished_updates,
                                         argument=(update_name,))
        else:
            # No update_time was specified. 2 options, do nothing or update,
            # can be changed in json
            if config['update_no_time_specified']:
                if covid_ud and news_ud:
                    logger.info('User calls for immediate news and stats update'
                                )
                    c_news.update_news(config['ud_search_terms'])
                    c_data.update_stats()
                elif covid_ud:
                    logger.info('User calls for immediate stats update')
                    c_data.update_stats()
                elif news_ud:
                    logger.info('User calls for immediate news update')
                    c_news.update_news(config['ud_search_terms'])
            else:
                # User didn't ask for anything to be done. Do nothing.
                pass
    UpdateScheduler.run(blocking=False)
    continuous_testing()
    #  Receiving any arguments that are sent when the x buttons are triggered.
    update_to_cancel = request.args.get('update_item')
    article_to_delete = request.args.get('notif')
    if update_to_cancel:
        logger.info('User calls to cancel update: %s', update_to_cancel)
        # This actually cancels the update
        c_data.cancel_scheduled_stats_updates(update_to_cancel)
        # The following ensures the cancellation is represented in the user_interface
        # record.
        for update in ui_scheduled_updates:
            if update['title'] == update_to_cancel:
                ui_scheduled_updates.remove(update)
    if article_to_delete:
        c_news.remove_article(article_to_delete)
        logger.info('User calls to delete news article: %s', article_to_delete)
    return render_template('index.html',
                           location=ud_location,
                           nation_location="England",
                           local_7day_infections=c_data.stats["L7DIR"],
                           national_7day_infections=c_data.stats["N7DIR"],
                           hospital_cases=c_data.stats["CHCases"],
                           deaths_total=c_data.stats["TD"],
                           news_articles=c_news.news_articles,
                           updates=ui_scheduled_updates)


if __name__ == '__main__':
    app.run()
