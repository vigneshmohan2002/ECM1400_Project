from flask import Flask
from flask import render_template
import covid_data_handler
import covid_news_handling

app = Flask(__name__)

# Use config.json to set ud_location and ud_location_type.
# Check if ud_location is defined and call function accordingly

ud_location = ""
ud_location_type = ""

"""
Coding Tip:
# Run code to find covid stats here (outside the "@app.route('/')" decorator)
# to update the dashboard stats and news. Use global variables?
# Generate the values here and display it in the dashboard inside the
# "@app.route('/')" decorator
"""

stats = {}  # This variable gets displayed, changes are made to this
news = {}  # This variable gets displayed, changes are made to this

# Update for covid stats to be displayed in dashboard when it's initially
# opened. This prevents continuous refresh of stats. After this the scheduled
# updates will handle it.

if ud_location == "":
    ud_location = "Exeter"
    stats = covid_data_handler.covid_API_request()
else:
    stats = covid_data_handler.covid_API_request(ud_location,
                                                 ud_location_type)

# Update for the news to display in dashboard when it's initially opened.
# This prevents continuous refresh of news.

news = covid_news_handling.update_news()


@app.route('/')
def updates():
    """
    This function shall run all the updating functions i.e those for covid stats
    and news. Since the page refreshes every 60 seconds this function will be
    run. This only runs the scheduling functions so the covid stats and news
    will be run when the time that is set for it is reached. The refresh simply
    leads to the time being checked.
    """
    return render_template('index.html',
                           location=ud_location,
                           nation_location="England",
                           local_7day_infections=stats["L7DIR"],
                           national_7day_infections=stats["N7DIR"],
                           hospital_cases=stats["CHCases"],
                           deaths_total=stats["TD"])

# The following decorator is reached when any button is pressed.
# When the "Submit" button is pressed the request triggered is update
# When the "Scheduled updates X" button is pressed the request triggered is
# update_item
# When the "News headlines X" button is pressed the request triggered is notif


@app.route('/index')
def button_response():
    return render_template('index.html',
                           location=ud_location,
                           nation_location="England",
                           local_7day_infections=stats["L7DIR"],
                           national_7day_infections=stats["N7DIR"],
                           hospital_cases=stats["CHCases"],
                           deaths_total=stats["TD"])


if __name__ == '__main__':
    app.run()
