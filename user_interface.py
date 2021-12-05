from flask import Flask
from flask import render_template
from flask import request
from flask import redirect as rd, url_for
import covid_data_handler as c_data
import covid_news_handling as c_news
from utils import json_processor, UpdateScheduler
import logging

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
c_news.update_news()

ui_scheduled_updates = []


def removing_finished_updates(finished_update: str) -> None:
    for update in ui_scheduled_updates:
        if update['title'] == finished_update:
            ui_scheduled_updates.remove(update)
    return None


@app.route('/')
def redirect():
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
    update_name = request.args.get('two')  # Always filled.
    update_time = request.args.get('update')
    repeat = request.args.get('repeat')
    covid_ud = request.args.get('covid-data')
    news_ud = request.args.get('news')
    # This will be run if the Submit button is triggered.
    if update_name:
        if update_time:
            # Each if statement here corresponds to whether both the news and
            # stats update checkboxes were triggered or if either one was
            # triggered.
            if covid_ud and news_ud:  # Stats and News checkboxes
                if repeat:
                    update_name = update_name + ' (News and statistics)' + \
                                  '(Repeating)'
                    c_data.schedule_covid_updates(update_name, update_time,
                                                  repeating=True)
                    c_news.schedule_news_updates(update_name, update_time,
                                                 repeating=True)
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                    logger.info('User tries to schedule update: %s',
                                update_name)
                else:
                    update_name = update_name + ' (News and statistics)'
                    c_data.schedule_covid_updates(update_name, update_time)
                    c_news.schedule_news_updates(update_name, update_time)
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                    # Scheduling the removal after it's performed
                    UpdateScheduler.enter(update_time, 3,
                                          removing_finished_updates,
                                         argument=(update_name,))
                    logger.info('User tries to schedule update: %s',
                                update_name)
            elif covid_ud:  # Stats checkbox
                if repeat:
                    update_name = update_name + ' (Statistics)(Repeating)'
                    c_data.schedule_covid_updates(update_name, update_time,
                                                  repeating=True)
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                    logger.info('User tries to schedule update: %s',
                                update_name)
                else:
                    update_name = update_name + ' (Statistics)'
                    c_data.schedule_covid_updates(update_name, update_time)
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                    # Scheduling the removal after it's performed
                    UpdateScheduler.enter(update_time, 3,
                                          removing_finished_updates,
                                         argument=(update_name,))
                    logger.info('User tries to schedule update: %s',
                                update_name)
            elif news_ud:  # News checkbox
                if repeat:
                    update_name = update_name + ' (News)(Repeating)'
                    c_news.schedule_news_updates(update_name, update_time,
                                                 repeating=True)
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                    # UpdateScheduler.enter(update_time, 3,
                    #                       removing_finished_updates,
                    #                      argument=(update_name,))
                    logger.info('User tries to schedule update: %s',
                                update_name)
                else:
                    update_name = update_name + ' (News)'
                    c_news.schedule_news_updates(update_name, update_time)
                    ui_scheduled_updates.append({'title': update_name,
                                                 'content': update_time})
                    # Scheduling the removal after it's performed
                    UpdateScheduler.enter(update_time, 3,
                                          removing_finished_updates,
                                         argument=(update_name,))
                    logger.info('User tries to schedule update: %s',
                                update_name)
        else:
            # No update_time was specified. 2 options, do nothing or update,
            # can be changed in json
            if config['update_no_time_specified']:
                if covid_ud and news_ud:
                    c_news.update_news()
                    c_data.update_stats()
                    logger.info('User calls for news and stats update')
                elif covid_ud:
                    c_data.update_stats()
                    logger.info('User calls for stats update')
                elif news_ud:
                    c_news.update_news()
                    logger.info('User calls for news update')
    UpdateScheduler.run(blocking=False)
    #  Receiving any arguments that are sent when the x buttons are triggered.
    update_to_cancel = request.args.get('update_item')
    article_to_delete = request.args.get('notif')
    if update_to_cancel:
        # This actually cancels the update
        c_data.cancel_scheduled_stats_updates(update_to_cancel)
        # The following ensures the cancellation is represented in the list
        # Loop to find the dictionary representing the update and removing it.
        for update in ui_scheduled_updates:
            if update['title'] == update_to_cancel:
                ui_scheduled_updates.remove(update)
        logger.info('User calls to cancel update: %s', article_to_delete)
    if article_to_delete:
        # This will update the global articles list used in the news module
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
