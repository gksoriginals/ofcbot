import os
import requests
from dotenv import load_dotenv
from jb_client import JBClient

load_dotenv(
    "ops/.env"
)

CUSTOM_NAME = os.getenv("CUSTOM_NAME")

class OFCAgent:
    def __init__(self, username, language, uuid, history=[]):
        self.client = JBClient(language, uuid, str(history))
        self.username = username
        self.language = language
        self.history = history

    def get_agent_state(self):
        return {
            "username": self.username,
            "language": self.language,
            "uuid": self.client.uuid,
            "history": self.history
        }

    def compose_welcome_message(self):
        if self.language == "English":
            return (
                f"Hi {self.username}, I am {CUSTOM_NAME} bot, "
                "your friendly AI powered bot to answer your queries. "
                "Please be advised not to take these AI as "
                "standard/correct information. Always consult with the concerned "
                "personnel for availing relevant information."
            )
        elif self.language == "Hindi":
            return (
                f"नमस्ते {self.username}, मैं {CUSTOM_NAME} बॉट हूँ, "
                "आपके प्रश्नों का उत्तर देने के लिए आपका मित्र ए.आई. पावर्ड बॉट। "
                "कृपया ध्यान दें कि इन ए.आई. को मानक/सही जानकारी के रूप में न लें। "
                "संबंधित जानकारी प्राप्त करने के लिए हमेशा संबंधित कर्मचारियों से परामर्श करें।"
            )
        elif self.language == "Kannada":
            return (
                f"ಹಲೋ {self.username}, ನಾನು {CUSTOM_NAME} ಬಾಟ್, "
                "ನಿಮ್ಮ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರ ನೀಡಲು ನಿಮ್ಮ ಸ್ನೇಹಿತ ಏ.ಐ. ಶಕ್ತಿಯ ಬಾಟ್. "
                "ಈ ಏ.ಐ. ಗಳನ್ನು ಮಾನಕ/ಸರಿಯಾದ ಮಾಹಿತಿಯಾಗಿ ತೆಗೆದುಕೊಳ್ಳಬೇಡಿ. "
                "ಸಂಬಂಧಿತ ಮಾಹಿತಿಯನ್ನು ಪಡೆಯಲು ಯೋಗ್ಯವಾದ ವ್ಯಕ್ತಿಗಳೊಂದಿಗೆ ಸಂಪರ್ಕಿಸಿ."
            )
        
    def update_conversation(self, user_message, bot_message):
        self.history.append(
            {
                "user_message": user_message,
                "bot_message": bot_message
            }
        )
        return self.history
    
    def get_bot_response(self, user_message, voice):
        if voice:
            response = self.client.voice_inference(user_message)
        else:
            response = self.client.text_inference(user_message)
        return response
    
    def get_action_options(self, user_input):
        english_options = {
            "action_1": "I want information on legal rights",
            "action_2": "I want to raise a complaint",
            "action_3": "I am not sure",
        }
        hindi_options = {
            "action_1": "मुझे कानूनी अधिकारों पर जानकारी चाहिए",
            "action_2": "मैं शिकायत दर्ज करना चाहता हूँ",
            "action_3": "मुझे अधिक जानकारी चाहिए",
        }
        kannada_options = {
            "action_1": "ನನಗೆ ನ್ಯಾಯಿಕ ಹಕುಗಳ ಮಾಹಿತಿ ಬೇಕಾಗಿದೆ",
            "action_2": "ನಾನು ತಪ್ಪಿಸುವ ವಿನಂತಿಯನ್ನು ಹೇಳಬಯಸುತ್ತೇನೆ",
            "action_3": "ನನಗೆ ಖಚಿತವಾಗಿ ಗೊತ್ತಿಲ್ಲ",
        }
        options = {
            "English": english_options,
            "Hindi": hindi_options,
            "Kannada": kannada_options,
        }
        return options.get(self.language, english_options).get(user_input, "Invalid action")
    
    def get_wait_message(self):
        english_message = "Thank you, allow me to search for the best information to respond to your query."
        hindi_message = "धन्यवाद, मैं आपके प्रश्न का उत्तर देने के लिए सर्वोत्तम जानकारी खोजने की अनुमति दें."
        kannada_message = "ಧನ್ಯವಾದಗಳು, ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರ ಕೊಡಲು ಉತ್ತಮ ಮಾಹಿತಿಯನ್ನು ಹುಡುಕಲು ನನಗೆ ಅನುಮತಿಸಿ."
        messages = {
            "English": english_message,
            "Hindi": hindi_message,
            "Kannada": kannada_message,
        }
        return messages.get(self.language, english_message)


    def parse_bot_response(self, bot_response):
        if "error" in bot_response:
            return "An error has been encountered. Please try again.", None
        if 'audio_output_url' in bot_response:
            audio_output_url = bot_response['audio_output_url']
            if audio_output_url != "":
                audio_request = requests.get(audio_output_url)
                audio_data = audio_request.content
                return bot_response["answer"], audio_data
        return bot_response["answer"], None
    
    def split_message(self, message):
        return message.split("\n")
    
    def execute(self, user_message, voice=False):
        if not self.history:
            bot_message = self.compose_welcome_message()
            history = self.update_conversation(user_message, bot_message)
            return [bot_message], None, history
        bot_response = self.get_bot_response(user_message, voice)
        bot_message, audio_data = self.parse_bot_response(bot_response)
        bot_messages = self.split_message(bot_message)
        history = self.update_conversation(user_message, bot_message)
        return bot_messages, audio_data, history


    
