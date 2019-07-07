"""Functions to manage saving of iDBL data."""
import json
from pathlib import Path


def upload_to_api(data, session, api_url):
    """Uploads the extracted data via the API."""

def save_html_to_file(html, path, abc_id):
    """Saves the HTML data to file."""
    file_path = Path(path, abc_id).with_suffix('html')

    with open(file_path, 'rb') as html_file:
        html_file.write(html)

def save_api_data_to_file(data, path, abc_id):
    """Saves the extracted API data to file."""
    file_path = Path(path, abc_id).with_suffix('json')

    with open(file_path, 'rb') as api_file:
        json.dump(data, api_file)

def save_idbl_data(idbl_data, session, settings):
    """Saves the provided iDBL data."""
    # Upload data via API (if enabled)
    if settings['data_upload']:
        upload_to_api(idbl_data.data, session, settings['api_url'])

    # Save raw HTML data to file (if enabled)
    if settings['files']['save_html']:
        save_html_to_file(
            idbl_data.data, settings['files']['save_html'], idbl_data.abc_id
        )

    # Save API data to file (if enabled)
    if settings['files']['save_api']:
        save_api_data_to_file(
            idbl_data.data, settings['files']['save_html'], idbl_data.abc_id
        )

def clear_old_record(abc_id, session, settings):
    """Removes any old records for provided ID from database."""
    if settings['data_upload']:
        pass
