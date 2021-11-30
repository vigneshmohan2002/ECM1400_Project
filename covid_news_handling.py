import requests
from miscellaneous import json_processor, UpdateScheduler


config = json_processor('config.json')

# Global variable that will be accessed here and in user_interface module
news_articles = []
scheduled_news_updates = {}
removed_articles = set()
ud_search_terms = config['ud_search_terms']


def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
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


def update_news_repeating():
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
    UpdateScheduler.enter(24*60*60, 1, update_news_repeating)
    return None


def remove_article(del_article_title):
    for article in news_articles:
        if article["title"] == del_article_title:
            news_articles.remove(article)
    removed_articles.add(del_article_title)
    return None


def schedule_news_updates(update_name: str, update_interval: int):
    scheduled_news_updates.update({update_name: UpdateScheduler.enter
    (update_interval, 1, update_news)})


def schedule_repeating_news_updates(update_name: str, update_interval: int):
    scheduled_news_updates.update({update_name: UpdateScheduler.enter
    (update_interval, 1, update_news_repeating)})


def cancel_scheduled_news_updates(update_name: str):
    try:
        UpdateScheduler.cancel(scheduled_news_updates[update_name])
        del scheduled_news_updates[update_name]
    except KeyError:
        pass
