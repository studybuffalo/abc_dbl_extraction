"""Functions and variables for configuration."""
from pathlib import Path

import configparser

from modules.exceptions import ImproperlyConfigured

def _resolve_if_path_needed(use_flag, path_string):
    """Determines if a path is needed and if it is valid."""
    if use_flag:
        path = Path(path_string)

        if path.exists() and path.is_dir():
            return path

        raise ImproperlyConfigured(
            'Invalid path string provided.'
        )

    return False

def get_settings(command_line_args):
    """Compiles all relevant settings for application."""
    ini_location = command_line_args['config']
    config = configparser.ConfigParser()
    config.read(ini_location)

    # Add the settings from the ini file
    settings = {}

    try:
        settings['crawl_delay'] = config.getfloat('settings', 'crawl_delay')
        settings['api_url'] = config['settings']['api_url']
        settings['api_authorization'] = 'Token {}'.format(
            config['settings']['api_token']
        )
        settings['abc_url'] = config['settings']['abc_url']
        settings['abc_id_start'] = config.getint('settings', 'abc_id_start')
        settings['abc_id_end'] = config.getint('settings', 'abc_id_end')
        settings['abc_id_increment'] = config.getint(
            'settings', 'abc_id_increment'
        )
        settings['robot'] = {
            'user_agent': config['robot']['user_agent'],
            'from': config['robot']['from'],
        }
        settings['extracted_data'] = {
            'html': config['locations']['html'],
            'api': config['locations']['api'],
        }
        settings['sentry'] = config['sentry']['dsn']

    except (configparser.Error, KeyError) as error:
        raise ImproperlyConfigured(error)

    # Check if use_html location is needed
    files = {}
    files['use_html'] = _resolve_if_path_needed(
        command_line_args['use_html_file'], config['locations']['html']
    )
    files['save_html'] = _resolve_if_path_needed(
        command_line_args['save_html'], config['locations']['html']
    )
    files['save_api'] = _resolve_if_path_needed(
        command_line_args['save_api'], config['locations']['api']
    )
    settings['files'] = files

    # Add the other command line arguments
    settings['data_upload'] = not command_line_args['disable_data_upload']

    return settings
