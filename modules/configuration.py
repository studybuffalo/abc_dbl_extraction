"""Functions and variables for configuration."""
import configparser

from modules.exceptions import ImproperlyConfigured

class Configuration:
    """Handles all relevant settings/configuration details."""
    def __init__(self, command_line_args):
        self.settings = self._get_settings(command_line_args)

    def open_files(self):
        """If needed, opens any files for use."""

    def close_files(self):
        """If needed, closes any open files."""

    def _get_settings(self, command_line_args):
        """Compiles all relevant settings for application."""
        ini_location = command_line_args['config']
        config = configparser.ConfigParser()
        config.read(ini_location)

        # Add the settings from the ini file
        settings = {}

        try:
            settings['crawl_delay'] = config['settings']['crawl_delay']
            settings['api_url'] = config['settings']['api_url']
            settings['abc_url'] = config['settings']['abc_url']
            settings['abc_pdf_url'] = config['settings']['abc_pdf_url']
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

        # Add the command line arguments
        settings['abc_start_id'] = command_line_args['start_id']
        settings['abc_end_id'] = command_line_args['end_id']
        settings['upload'] = {
            'data': not command_line_args['disable_data_upload'],
            'sub': not command_line_args['disable_sub_upload'],
        }
        settings['save'] = {
            'html': command_line_args['save_html'],
            'api': command_line_args['save_api'],
        }
        settings['source'] = {
            'site_html': not command_line_args['use_html_file'],
        }

        return settings
