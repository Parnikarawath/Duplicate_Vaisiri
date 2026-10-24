import requests


def get_news():
    try:
        url = 'https://newsapi.org/v2/top-headlines?sources=the-times-of-india&apiKey=ae5ccbe2006a4debbe6424d7e4b569ec'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            news_dict = response.json()
            if news_dict.get('status') == 'ok':
                return news_dict.get('articles', [])
        return []
    except Exception as e:
        print(f"News fetch error: {e}")
        return []
