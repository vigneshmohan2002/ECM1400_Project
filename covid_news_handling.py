import requests

news_articles = []
removed_articles = set()
# Use config.json to set ud_search_terms.
ud_search_terms = ""


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
        if not(article["url"] in removed_articles):
            news_articles.append((article["title"], article["url"],
                                  article["content"][:100]))
    return news_articles


def remove_article(del_article_url):
    for article in news_articles:
        if article["url"] == del_article_url:
            news_articles.remove(article)
    removed_articles.add(del_article_url)
