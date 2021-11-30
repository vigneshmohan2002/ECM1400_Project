import requests
from miscellaneous import json_processor, UpdateScheduler


config = json_processor('config.json')

# Global variable that will be accessed here and in user_interface module
news_articles = []
scheduled_news_updates = {}
removed_articles = set()
ud_search_terms = config['ud_search_terms']


def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    """
    This function is used to access the News API to pull articles passing the
    necessary search terms in the query and return articles related to those
    terms.

    :param covid_terms: Search terms passed into the function
    :return results["articles"]: Returns the values attributed to articles key
    in the dictionary generated from the json file pulled from the API.
    """
    url = 'https://newsapi.org/v2/everything?'
    search_terms = covid_terms.split()
    results = {}
    for term in search_terms:
        parameters = {
            'q': term,
            'pageSize': 20,
            'apiKey': 'def57b93404d42e498143fe854a78caf',
        }
        results = requests.get(url, params=parameters).json()
    return results["articles"]


def update_news():
    """
    This function updates the global news_articles variable that is accessed by
    the user_interface module when scheduled.
    """
    if ud_search_terms == "":
        articles_to_be_processed = news_API_request()
    else:
        articles_to_be_processed = news_API_request(ud_search_terms)
    for article in articles_to_be_processed:
        if not(article["title"] in removed_articles):
            news_articles.append({'title': article["title"],
                                  'content': article["content"][:100],
                                  'url': article["url"]
                                  })
    return None


def update_news_repeating(update_name):
    """
    This function updates the global news_articles variable that is accessed by
    the user_interface module when scheduled. It also schedules itself to run
    again in 24 hours under the same update name so that it may be canceled if
    requested by the user.

    :param update_name: The name of the update
    """
    if ud_search_terms == "":
        articles_to_be_processed = news_API_request()
    else:
        articles_to_be_processed = news_API_request(ud_search_terms)
    for article in articles_to_be_processed:
        if not(article["url"] in removed_articles):
            news_articles.append({'title': article["title"],
                                  'content': article["content"][:100] +
                                             "Read More:" + article["url"]
                                  })
    task = UpdateScheduler.enter(24*60*60, 1, update_news_repeating,
                                 argument=update_name)
    scheduled_news_updates.update({update_name: task})
    return None


def remove_article(del_article_title):
    """
    This function removes articles from the global news_articles variable
    according to the title of the article.
    :param del_article_title: The title of the article to be removed.
    """
    for article in news_articles:
        if article["title"] == del_article_title:
            news_articles.remove(article)
    removed_articles.add(del_article_title)
    return None


def schedule_news_updates(update_name: str, update_interval: int):
    """
    This function schedules updates to the news_articles variable using the
    scheduler.enter() function from the sched module and the update_news
    function.
    :param update_name: The name of the update
    :param update_interval: The interval to pass into the scheduler.enter
    function
    """
    scheduled_news_updates.update({update_name: UpdateScheduler.enter
    (update_interval, 1, update_news)})


def schedule_repeating_news_updates(update_name: str, update_interval: int):
    """
    This function schedules repeating updates to the news_articles variable
    using the scheduler.enter() function from the sched module and the
    update_news_repeating function.

    :param update_name: The name of the update
    :param update_interval: The interval to pass into the scheduler.enter
    function
    """
    scheduled_news_updates.update({update_name: UpdateScheduler.enter
    (update_interval, 1, update_news_repeating, argument=update_name)})


def cancel_scheduled_news_updates(update_name: str):
    """
    This function cancels scheduled updates to the news variable using the
    scheduler.cancel() function from the sched module and accessing the global
    scheduled_news_updates dictionary.

    :param update_name: The name of the update
    """
    try:
        UpdateScheduler.cancel(scheduled_news_updates[update_name])
        del scheduled_news_updates[update_name]
    except KeyError:
        pass
