import requests
from twilio.rest import Client

import config

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

av_api_key = config.AV_API_KEY
news_api_key = config.NEWS_API_KEY
twilio_account_sid = config.TWILIO_ACCOUNT_SID
twilio_auth_token = config.TWILIO_AUTH_TOKEN

message = f"{STOCK}: "

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": av_api_key,
}
response_stock = requests.get(url=STOCK_ENDPOINT, params=stock_params)
response_stock.raise_for_status()
data_stock = response_stock.json()["Time Series (Daily)"]

data_list = [value for (key, value) in data_stock.items()]
yesterday_closing_price = float(data_list[0]["4. close"])
before_yesterday_closing_price = float(data_list[1]["4. close"])

percentage = round(
    number=((yesterday_closing_price - before_yesterday_closing_price) * 100) / before_yesterday_closing_price,
    ndigits=2
)
if percentage >= 0:
    message += f"🔺{percentage}%"
else:
    message += f"🔻{-percentage}%"

if abs(percentage) >= 0:
    news_params = {
        "qInTitle": COMPANY_NAME,
        "from": "2024-01-21",
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": news_api_key,
    }
    response_news = requests.get(url=NEWS_ENDPOINT, params=news_params,)
    response_news.raise_for_status()
    data_news = response_news.json()["articles"]

    three_articles = data_news[:3]
    for article in three_articles:
        message += f"\nHeadline: {article['title']}\nBrief: {article['description']}\n"

    client = Client(twilio_account_sid, twilio_auth_token)
    sms_message = client.messages \
        .create(
            body=message,
            from_=config.TWILIO_PHONE_N,
            to=config.MY_PHONE_N
        )
    print(sms_message.status)
