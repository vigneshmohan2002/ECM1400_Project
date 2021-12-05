import requests
from utils import json_processor, UpdateScheduler, current_time_hhmmss
from utils import required_interval as interval
import logging

# Logger initialization
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('ProjectLogFile.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

config = json_processor('config.json')


# Global variable that will be accessed here and in user_interface module
news_articles = []
scheduled_news_updates = {}
removed_articles = set()
ud_search_terms = config['ud_search_terms']


def news_API_request(covid_terms: str = "Covid COVID-19 coronavirus") -> dict:
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
    pagesize = config['number_of_articles_on_the_page']
    for term in search_terms:
        parameters = {
            'q': term,
            'pageSize': pagesize,
            'apiKey': 'def57b93404d42e498143fe854a78caf',
        }
        results = requests.get(url, params=parameters).json()
    logger.info('News API accessed')
    return results["articles"]


def update_news() -> None:
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
    logger.info('news_articles updated')
    return None


def update_news_repeat(update_name: str) -> None:
    """
    This function updates the global news_articles variable that is accessed by
    the user_interface module when scheduled. It also schedules itself to run
    again in 24 hours under the same update name so that it may be canceled if
    requested by the user.

    :param update_name: The name of the update
    """
    print("update_repeat_news marker")
    print("called at:" + current_time_hhmmss())
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
    # Changed to 60 for testing change back to 24*60*60
    task = UpdateScheduler.enter(60, 2, update_news_repeat,
                                argument=(update_name, ))
    scheduled_news_updates.update({update_name: task})
    logger.info('news_articles updated')
    return None


def remove_article(del_article_title: str) -> None:
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


def schedule_news_updates(update_name: str, update_time: str = "",
                          update_interval: int = 0,
                          repeating: bool = False,
                          repeat_interval: int = 24*60*60) -> None:
    """
    This function schedules updates to the news_articles variable using the
    scheduler.enter() function from the sched module and the update_news
    function.
    :param update_name: The name of the update
    :param update_interval: The interval to pass into the scheduler .enter
    function
    :param update_time: The time used to generate the interval to pass into the
    scheduler.enter function
    :param repeating: Whether the update is repeating or not.
    :param repeat_interval: The interval between repeats for repeating updates
    """
    if update_time != "":
        update_interval = interval(update_time)
    if repeating:
        scheduled_news_updates.update({update_name: UpdateScheduler.enter
        (update_interval, 2, update_news)})
        logger.info('News update scheduled for %s, delay: %s', update_time,
                    str(update_interval))
    else:
        scheduled_news_updates.update({update_name: UpdateScheduler.enter
        (update_interval, 2, update_news_repeat,
         argument=(update_name, repeat_interval))})
        logger.info('Repeating news update scheduled for %s, delay: %s',
                    update_time, str(update_interval))
    return None


def cancel_scheduled_news_updates(update_name: str) -> None:
    """
    This function cancels scheduled updates to the news variable using the
    scheduler.cancel() function from the sched module and accessing the global
    scheduled_news_updates dictionary.

    :param update_name: The name of the update
    """
    try:
        UpdateScheduler.cancel(scheduled_news_updates[update_name])
        del scheduled_news_updates[update_name]
        logger.info('%s update cancelled.', update_name)
    except KeyError:
        logger.warning('Key error was thrown')
        pass
    except ValueError:
        # This will be run in the off chance that an update that has been
        # finished isn't removed before the refresh. The scheduler is run again,
        # this allows it to remove the finished update.
        logger.warning('Refresh occurred before %s was cancelled', update_name)
        UpdateScheduler.run()
    return None
