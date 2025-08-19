import os

class Config(object):
    # API credentials
    API_ID = int(os.environ.get("API_ID", 27744634))  # Replace with your actual API ID
    API_HASH = os.environ.get("API_HASH", "0db310b3f4e8b07d938bcf2295bcb03d")  # Replace with your actual API Hash
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7585807006:AAF0JY0e2ZZBGHJ7ZQSL_-90fuU_TShLt6U")  # Replace with your actual Bot Token

    # Authorized users
    AUTHORIZED_USERS = list(int(x) for x in os.environ.get("AUTH_USERS", "8078418903").split(" "))  # Replace with actual user IDs

    # Owner ID
    OWNER_ID = int(os.environ.get("OWNER_ID", 8078418903))  # Replace with your actual Owner ID

    # Download directory
    DOWNLOAD_DIRECTORY = os.environ.get("DOWNLOAD_DIRECTORY", "./downloads")  # Default download directory

