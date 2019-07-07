"""Functions to manage saving of iDBL data."""
def upload_to_api(data, session, api_url):
    """Uploads the extracted data via the API."""

def save_html_to_file(html, path, abc_id):
    """Saves the HTML data to file."""

def save_api_data_to_file(data, path, abc_id):
    """Saves the extracted API data to file."""

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
