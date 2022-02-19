# py-twitter-api

A Twitter API wrapper for Python (that actually works - maybe).

# info for usage

## set up a Twitter object

Start by instantiating a new `Twitter` instance:

```py
my_app = Twitter(
    oauth_client_id = "oauth_client_id",
    oauth_client_secret = "oauth_client_secret"
)
```

`oauth_client_id` and `oauth_client_secret` are found in your bot's dashboard, under "User authentication settings" (OAuth 2.0 will need to be enabled).

Default scopes are `tweet.read` and `users.read`. If you need more scopes, add `scopes = ["scope.1", "scope.2", ...]` to your `Twitter` object.

Default redirect URI is `http://localhost/`. If the URI does not match this exactly (including the trailing `/`), add `redirect_uri = "http://my_redirect_uri.com"` to your `Twitter` object.

## getting authenticated

**currently, only OAuth2 is supported for authentication, but I do plan on adding other methods soon.**

### getting an authorization url
With your `Twitter` object set up and matching your bot settings, call `get_auth_url()`. This returns a URL that your user must follow to use your app **(app-only authentication coming soon)**.

```py
url = my_app.get_auth_url()
print(url) # https://twitter.com/i/oauth2/authorize?...
```

### getting an access token
Once the user accepts the authorization request, you must have a server set up to accept a callback. For example, if your redirect URI is set to `http://localhost:3000`, then you need to have a server listening there.

When the user is redirected to your callback, feed the request URL to `get_access_token()`. It contains the necessary information to get an access token.

```py
# using Flask for this example

@server.route("/")
def index():
    my_app.get_access_token(request.url)
    return "<h1>Authorized!</h1>"
```

The access token and refresh token (which is only obtainable if you add "offline.access" to your scopes) can be used with `my_app.access_token` and `my_app.refresh_token`.

### refreshing an access token
Access tokens expire after 2 hours. If you need to refresh it, call `get_refresh_token()`.

```py
my_app.get_refresh_token()
```

### revoking tokens

If you want a token invalidated for secuity purposes (e.g logging out a user), call `revoke_token()`. It will invalidate both the access token and the refresh token.

```py
my_app.revoke_token()

print(my_app.access_token) # None
print(my_app.refresh_token) # None
```

## tweet-related methods

### sending tweets

Sending tweets requires the following scopes:

* `tweet.read`
* `tweet.write`
* `users.read`

Call `send_tweet()`:

```
my_app.send_tweet("Hello, world!") # {"data": {"id": ...}}
```

*More features, including attachments, location information, Super Follower-exclusive tweets, polls, and more will be added soon.*