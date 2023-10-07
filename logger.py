import logging
import inspect
from datetime import datetime
from database import store_error_in_db

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(error_message):
    timestamp = datetime.now()
    # Get the name of the function and file where the error occurred
    caller_frame = inspect.stack()[1]
    file_name = caller_frame.filename
    function_name = caller_frame.function
    logging.error(error_message)
    store_error_in_db(error_message, timestamp, file_name, function_name)
