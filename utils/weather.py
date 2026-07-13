import requests

API_KEY = "1355dc2ea9e0d562c9b6a6dea5100eaa"
CITY = "Tashkent"


def get_weather():

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={CITY}"
        f"&appid={API_KEY}"
        "&units=metric"
    )

    try:
        return requests.get(url, timeout=10).json()
    except Exception:
        return {"cod": 500}