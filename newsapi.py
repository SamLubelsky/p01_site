from urllib.request import urlopen
import json
import requests
startpoint = "https://newsapi.org/v2"
api_key = ""
with open("keys/key_newsapi.txt", 'r') as k:
    api_key = k.read().strip()


def request_articles(query, n=1):
    if len(query.split(' ')) > 1:
        query = "%20".join(query.split(' '))
    url = f"{startpoint}/everything?q={query}&language=en&apiKey={api_key}"
    # req = requests.get(startpoint + "/everything", params = {
    #     'q': query,
    #     'language': 'en',
    #     'apiKey': api_key
    # })
    # return req.content
    return request(url, n)


def request_top_headlines(category, n=10):
    url = f"{startpoint}/top-headlines?category={category}&language=en&apiKey={api_key}"
    return request(url, n)


def request(url, n):
    response = urlopen(url)
    data_json = json.loads(response.read())
    return data_json["articles"][:n]


def article_info(article):
    return {
        "url": article["url"],
        "image": article["urlToImage"],
        "title": article["title"],
        "description": article["description"],
        "date": article["publishedAt"][:10],
        "author": article["author"]
    }


# if __name__ == "__main__":
#     articles = request_articles("bitcoin", 3)
#     for article in articles:
#         info = article_info(article)
#         print(info)
