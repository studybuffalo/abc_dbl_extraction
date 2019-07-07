"""Functions to manage saving of iDBL data."""
from datetime import datetime
import json
from pathlib import Path


class CustomJSONEncoder(json.JSONEncoder):
    """Extending JSONEncoder to support datetimes."""
    def default(self, o): # pylint: disable=method-hidden
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d')

        return json.JSONEncoder.default(self, o)

def upload_to_api(idbl_data, session, api_url):
    """Uploads the extracted data via the API."""
    # Assemble the API url
    api_url = '{}{}/'.format(api_url, idbl_data.abc_id)

    # Make the request
    response = session.post(api_url, data=idbl_data.data)

    print(response)

def save_html_to_file(html, path, abc_id):
    """Saves the HTML data to file."""
    file_path = Path(path, str(abc_id)).with_suffix('.html')

    with open(file_path, 'w+') as html_file:
        html_file.write(html)

def save_api_data_to_file(data, path, abc_id):
    """Saves the extracted API data to file."""
    file_path = Path(path, str(abc_id)).with_suffix('.json')

    with open(file_path, 'w+') as api_file:
        json.dump(data, api_file, cls=CustomJSONEncoder)

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

def clear_old_record(abc_id, session, settings):
    """Removes any old records for provided ID from database."""
    if settings['data_upload']:
        # Assemble the API url
        api_url = '{}{}/remove/'.format(settings['api_url'], abc_id)

        # Make the request
        response = session.post(api_url)

        print(response)
