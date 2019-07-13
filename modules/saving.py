"""Functions to manage saving of iDBL data."""
import json
from pathlib import Path

from requests.exceptions import ConnectionError # pylint: disable=redefined-builtin
from sentry_sdk import capture_message

from modules.exceptions import APIError

def upload_to_api(idbl_data, session, api_url):
    """Uploads the extracted data via the API."""
    # Assemble the API URL
    api_url = '{}{}/upload/'.format(api_url, idbl_data.data['din'])

    # Make the request
    try:
        response = session.post(api_url, data=json.dumps(idbl_data.data))
    except ConnectionError as error:
        return APIError(error)

    if response.status_code != 201:
        error_message = 'STATUS CODE: {}\nERROR CONTENT:{}'.format(
            response.status_code, response.content
        )
        capture_message(error_message, level=30)

def save_html_to_file(html, path, abc_id):
    """Saves the HTML data to file."""
    file_path = Path(path, str(abc_id)).with_suffix('.html')

    with open(file_path, 'w+') as html_file:
        html_file.write(html)

def save_api_data_to_file(data, path, abc_id):
    """Saves the extracted API data to file."""
    file_path = Path(path, str(abc_id)).with_suffix('.json')

    with open(file_path, 'w+') as api_file:
        json.dump(data, api_file)

def save_idbl_data(idbl_data, session, settings):
    """Saves the provided iDBL data."""
    # Upload data via API (if enabled)
    if settings['data_upload']:
        upload_to_api(idbl_data, session, settings['api_url'])

    # Save raw HTML data to file (if enabled)
    if settings['files']['save_html']:
        save_html_to_file(
            idbl_data.raw_html,
            settings['files']['save_html'],
            idbl_data.abc_id
        )

    # Save API data to file (if enabled)
    if settings['files']['save_api']:
        save_api_data_to_file(
            idbl_data.data,
            settings['files']['save_html'],
            idbl_data.abc_id
        )
