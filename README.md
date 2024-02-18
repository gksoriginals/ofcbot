# Telegram-Integration-Jugalbandi

This is an accelerator pack for deploying a telegram bot which uses Jugalbandi APIs.

### Steps to install, run and deploy

1. Clone the repository
2. Install the dependencies using `pip install -r requirements.txt`
3. Create `.env` file inside ops directory and add the following variables
    ```
    TELEGRAM_BOT_TOKEN_KEY=<API_KEY>
    UUID_NUMBER=<UUID>
    CUSTOM_NAME=<CUSTOM_NAME_OF_BOT>
    ```
4. Run the app using `python telegram_bot.py`