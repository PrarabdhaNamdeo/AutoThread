import requests
import os
from dotenv import load_dotenv
load_dotenv()

get_token_url = "https://graph.threads.net/refresh_access_token"

get_token_params = {
    "grant_type": "th_refresh_token",
    "access_token": os.getenv("THREADS_ACCESS_TOKEN")

}

response = requests.get(get_token_url, params=get_token_params)
print(response.text)

user_response = requests.get(
    "https://graph.threads.net/v1.0/me",
    params={"access_token": os.getenv("THREADS_ACCESS_TOKEN")}
)
print(user_response.text)