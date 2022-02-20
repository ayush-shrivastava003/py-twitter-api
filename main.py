import requests
from base64 import b64encode
from urllib.parse import urlencode
from string import ascii_letters
import random
from json import dumps

class TwitterAPIError(Exception):
    pass

class Twitter():
    def __init__(
            self,
            # consumer_key: str,
            # consumer_secret: str,
            oauth_client_id: str, 
            oauth_client_secret: str,
            scopes: list = ["tweet.read", "users.read"],
            redirect_uri: str = "http://localhost/"
        ):

        self.client_id = oauth_client_id
        self.client_secret = oauth_client_secret

        self.scopes = scopes
        self.redirect_uri = redirect_uri

        self.code_challenge = None
        self.access_token = None
        self.refresh_token = None

        encoded_credentials = f"{self.client_id}:{self.client_secret}".encode()
        encoded_credentials = b64encode(encoded_credentials).decode('ascii')

        self.token_headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}"
        }
        self.request_headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

    def _random_str(self) -> str :
        return "".join(random.choice(ascii_letters) for _ in range(20))

    def _handle_request(self, url, headers, data, wants_token=False) -> dict:
        res = requests.post(url, headers=headers, data=data)
        info = res.json()
    
        if res.status_code in (200, 201):
            if wants_token:
                self.access_token = info["access_token"]
                self.request_headers["Authorization"] = f"Bearer {self.access_token}"
                
                if "offline.access" in self.scopes:
                    self.refresh_token = info["refresh_token"]
    
            return info
        else:
            raise TwitterAPIError(f"The Twitter API returned a status code of {res.status_code}. Received: {info}")

    def get_auth_url(self) -> str:
        self.code_challenge = self._random_str()
        state = self._random_str()

        query_string = urlencode({
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "plain"
        })

        return f"https://twitter.com/i/oauth2/authorize?{query_string}"

    def get_access_token(self, callback_url: str) -> dict:
        code = callback_url.split("&")[1].split("=")[1]

        data = {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "code_verifier": self.code_challenge
        }
        
        return self._handle_request("https://api.twitter.com/2/oauth2/token", self.token_headers, data, True)

    def get_refresh_token(self) -> dict:
        if not self.refresh_token:
            raise TwitterAPIError("You don't have a refresh token. It may have expired, been invalidated, or 'offline.access' is not in your scopes.")

        data = {
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
            "client_id": self.client_id
        }

        return self._handle_request("https://api.twitter.com/2/oauth2/token", self.token_headers, data, True)

    def revoke_token(self, is_access_token=True) -> None:
        data = {"client_id": self.client_id}

        if is_access_token:
            data["token"] = self.access_token
            data["token_type_hint"] = "access_token"
        elif not is_access_token and self.refresh_token != None:
            data["token"] = self.refresh_token
            data["token_type_hint"] = "refresh_token"
        
        self._handle_request("https://api.twitter.com/2/oauth2/revoke", self.token_headers, data)

        if is_access_token:
            self.access_token = None
        else:
            self.refresh_token = None

        if self.access_token or self.refresh_token:
            is_access_token = not is_access_token
            self.revoke_token(is_access_token=is_access_token)

    def Tweet(self):
        return Tweet(self)

class Tweet():
    def __init__(self, twitter_ref):
        self.data = {}
        self.twitter: Twitter = twitter_ref

    def text(self, text: str):
        self.data["text"] = text

    def for_super_followers(self, for_super: bool):
        self.data["for_super_followers_only"] = for_super

    def location_info(self, place_id):
        self.data["geo"] = {"place_id": place_id}

    def poll(self, duration: int, options: list):
        self.data["poll"] = {
            "duration_minutes": duration,
            "options": options
        }

    def quote_tweet(self, tweet_id: str):
        self.data["quote_tweet_id"] = tweet_id

    def reply(self, tweet_id: str, exclude: list = [], settings: str = None):
        self.data["reply"] = {
            "in_reply_to_tweet_id": tweet_id,
            "exclude_reply_user_ids": exclude,
        }

        if settings != None:
            self.data["reply_settings"] = settings

    def remove(self, key):
        del self.data[key]

    def send(self):
        return self.twitter._handle_request("https://api.twitter.com/2/tweets", self.twitter.request_headers, dumps(self.data))

    # def upload_media(self, file_size, file_type, file_binary):
    #     data = {
    #         "command": "INIT",
    #         "total_bytes": file_size,
    #         "media_type": file_type,
    #     }

    #     init_media_data = self.twitter._handle_request("https://upload.twitter.com/1.1/media/upload.json", self.twitter.request_headers, data)

    #     data = {

    #     }

