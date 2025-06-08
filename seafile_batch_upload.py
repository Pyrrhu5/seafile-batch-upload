import asyncio
from src.access_token import Token
from src.constants import USERNAME, PASSWORD
from src.upload import upload_folder

Token.set_api_key(USERNAME)
Token.set_api_secret(PASSWORD)

if __name__ == '__main__':
    asyncio.run(upload_folder())
