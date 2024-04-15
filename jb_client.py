import requests
import os
import urllib

with open("prompts/prompt.txt", "r") as f:
    PROMPT = f.read()

class JBClient:
    def __init__(self, language, uuid, history=""):
        self.base_url = "https://api.jugalbandi.ai/"
        self.voice_route = "query-using-voice-gpt4"
        self.text_route = "query-with-langchain-gpt4-custom-prompt"
        self.base_prompt = PROMPT + history
        self.language = language
        self.uuid = uuid

    def text_inference(self, text):
        try:
            if self.language == "English":
                params = {
                    'uuid_number': self.uuid,
                    'query_string': text,
                    'prompt': self.base_prompt,
                }

                url = f"{self.base_url}{self.text_route}?{urllib.parse.urlencode(params)}"
            else:
                params = {
                        'uuid_number': self.uuid,
                        'query_text': text,
                        'audio_url': "",
                        'input_language': self.language,
                        'output_format': 'Text',
                        'prompt': self.base_prompt,
                    }
                url = f"{self.base_url}{self.text_route}?{urllib.parse.urlencode(params)}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            return {'error': e}
        except (KeyError, ValueError):
            return {'error': 'Invalid response received from API'}
        
    def voice_inference(self, audio_url):
        try:
            params = {
                'uuid_number': self.uuid,
                'audio_url': audio_url,
                'input_language': self.language,
                'output_format': 'Voice',
                'prompt': self.base_prompt,
            }

            url = f"{self.base_url}{self.voice_route}?{urllib.parse.urlencode(params)}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            return {'error': e}
        except (KeyError, ValueError):
            return {'error': 'Invalid response received from API'}
    
