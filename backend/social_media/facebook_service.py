import requests

class FacebookService:
    def __init__(self, access_token):
        self.access_token = access_token
        self.api_url = 'https://graph.facebook.com/v18.0'

    def get_account_info(self):
        url = f"{self.api_url}/me?fields=id,name,email&access_token={self.access_token}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def post_content(self, message, page_id=None):
        # If posting to a page, you need a page access token
        url = f"{self.api_url}/me/feed?access_token={self.access_token}"
        data = {'message': message}
        if page_id:
            url = f"{self.api_url}/{page_id}/feed?access_token={self.access_token}"
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json() 