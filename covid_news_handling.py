import requests, json


def news_API_request(covid_terms="Covid COVID-19 coronavirus"):

    url = 'https://newsapi.org/v2/everything?'
    parameters = {
        'q': covid_terms,
        'pageSize': 20,
        'apiKey': 'def57b93404d42e498143fe854a78caf'
    }
    results = requests.get(url, params=parameters).json()
    print("****************************************")
    print(json.dumps(results))
    print("****************************************")

news_API_request()
