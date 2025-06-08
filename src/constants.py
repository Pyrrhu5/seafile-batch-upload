import os

from dotenv import load_dotenv

load_dotenv()

SEAFILE_SERVER = os.environ["SEAFILE_SERVER"]
USERNAME = os.environ["SEAFILE_ADMIN_USER"]
PASSWORD = os.environ["SEAFILE_ADMIN_PWD"]
LIBRARY_ID = os.environ["SEAFILE_LIBRARY_ID"]
LOCAL_FOLDER = os.environ["LOCAL_FOLDER"]
CONCURRENT_UPLOAD = int(os.getenv("CONCURRENT_UPLOAD", 20))

ERRORS_LOG_FILENAME = "error.log"
SUCCESS_LOG_FILENAME = "uploaded_files.log"
