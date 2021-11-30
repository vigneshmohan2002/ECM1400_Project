from flask import Flask
from flask import render_template
from flask import request, url_for
import covid_data_handler as c_data
import covid_news_handling as c_news
from miscellaneous import required_interval as interval, json_processor
from miscellaneous import UpdateScheduler

config = json_processor('config.json')  # Global variable since used throughout

app = Flask(__name__)

ud_location = config['ud_location']
ud_location_type = config['ud_location_type']

c_data.update_stats()
c_news.update_news()

ui_scheduled_updates = []


@app.route('/index')
def button_responses():
    """
    This function is responsible for running the web application. When any
    button is triggered, the arguments are received here and the necessary
    actions are taken.
    :return: An html file containing all the necessary information is
    uploaded to the server using the render_template function from the flask
    module.
    """
    # Receiving any arguments that are sent when the submit button is triggered.
    update_name = request.args.get('two')  # Always filled.
    update_time = request.args.get('update')
    repeating = request.args.get('repeat')
    covid_ud = request.args.get('covid-data')
    news_ud = request.args.get('news')
    # This will be run if the Submit button is triggered.
    if update_name:
        if update_time:
            # Each if statement here corresponds to whether both the news and
            # stats update checkboxes were triggered or if either one was
            # triggered.
            if covid_ud and news_ud:
                if repeating:
                    c_data.schedule_repeating_covid_updates(update_name +
                                        ' (News and statistics) (Repeating)',
                                                 interval(update_time))
                    c_news.schedule_repeating_news_updates(update_name +
                                        ' (News and statistics) (Repeating)',
                                                 interval(update_time))
                    ui_scheduled_updates.append({'title': update_name +
                                        ' (News and statistics) (Repeating)',
                                                 'content': update_time})
                else:
                    c_data.schedule_repeating_covid_updates(update_name +
                                                ' (News and statistics)',
                                                  interval(update_time))
                    c_news.schedule_repeating_news_updates(update_name +
                                                ' (News and statistics)',
                                                 interval(update_time))
                    ui_scheduled_updates.append({'title': update_name +
                                                ' (News and statistics)',
                                                 'content': update_time})
            elif covid_ud:
                if repeating:
                    c_data.schedule_repeating_covid_updates(update_name +
                                                ' (Statistics)(Repeating)',
                                                 interval(update_time))
                    ui_scheduled_updates.append({'title': update_name +
                                                 ' (Statistics)(Repeating)',
                                                 'content': update_time})
                else:
                    c_data.schedule_covid_updates(update_name + ' (Statistics)',
                                                 interval(update_time))
                    ui_scheduled_updates.append({'title': update_name +
                                                 ' (Statistics)',
                                                 'content': update_time})
            elif news_ud:
                if repeating:
                    c_news.schedule_repeating_news_updates(update_name +
                                                 ' (News)(Repeating)',
                                                 interval(update_time))
                    ui_scheduled_updates.append({'title': update_name +
                                                 ' (News)(Repeating)',
                                                 'content': update_time})
                else:
                    c_news.schedule_news_updates(update_name + ' (News)',
                                                 interval(update_time))
                    ui_scheduled_updates.append({'title': update_name +
                                                          ' (News)',
                                                 'content': update_time})
        else:
            # The programming flow reaching here indicates no update_time was
            # specified. 2 options, do nothing or update, can be changed in json
            if config['update_no_time_specified']:
                if covid_ud and news_ud:
                    c_news.update_news()
                    c_data.update_stats()
                elif covid_ud:
                    c_data.update_stats()
                elif news_ud:
                    c_news.update_news()

    UpdateScheduler.run(blocking=False)
    #  Receiving any arguments that are sent when the x buttons are triggered.
    update_to_cancel = request.args.get('update_item')
    article_to_delete = request.args.get('notif')
    if update_to_cancel:
        c_data.cancel_scheduled_stats_updates(update_to_cancel)
        del ui_scheduled_updates[update_to_cancel]
    if article_to_delete:
        # This will update the global articles list used in that module
        c_news.remove_article(article_to_delete)
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
