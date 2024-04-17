import requests
import re

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_html(self, text_description):
        prompt = f"Directly provide HTML code for the body of a {text_description}, using Tailwind CSS classes for styling. HTML code only, no additional text or explanations. Wrap the content in a div with an id of 'container'."
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo-instruct",
                "prompt": prompt,
                "temperature": 0.3,
                "max_tokens": 1024,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop": ["</div>"]
            }
        )
        return response