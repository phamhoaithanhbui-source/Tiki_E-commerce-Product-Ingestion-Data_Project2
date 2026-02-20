import os
import json
from config import SUCCESS_DIR, ERROR_DIR

# create directory if not created yet
os.makedirs(SUCCESS_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)


def write_success(data, batch_number):
    """
    Save successful products to JSON file.
    """
    if not data:
        return  # avoid creating empty file

    file_path = os.path.join(
        SUCCESS_DIR,
        f"products_{batch_number:03}.json"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def write_error(data, batch_number):
    """
    Save failed products with error reason.
    """
    if not data:
        return  #  avoid creating empty file

    file_path = os.path.join(
        ERROR_DIR,
        f"errors_{batch_number:03}.json"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)