"""An Alberta Blue Cross iDBL extraction tool.

    Last Update: 2019-Jul-06

    Copyright (c) Notices
        2019    Joshua R. Torrance  <joshua@torrance.io>

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of
    the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not,
    see <http://www.gnu.org/licenses/>.
"""
import sys
import time
import traceback

import click
import requests
import sentry_sdk
from tqdm import trange

from modules import get_settings, extract_data, save_idbl_data, exceptions


@click.command()
@click.argument('start-id', type=click.INT)
@click.argument('end-id', type=click.INT)
@click.option(
    '--config', default='extraction.ini', type=click.Path(exists=True),
    help='Path to the .ini config file.'
)
@click.option(
    '--disable-data-upload', is_flag=True, help='Disables data API upload.'
)
@click.option(
    '--save-html', is_flag=True, help='Save extracted HTML data to file.'
)
@click.option(
    '--save-api', is_flag=True, help='Save API request data to file.'
)
@click.option(
    '--use-html-file', is_flag=True, help='Uses extracted HTML file.'
)
def extract(**kwargs):
    """The Study Buffalo Alberta Blue Cross iDBL Extraction Tool.

        This tool extracts entries from the iDBL, from START_ID to
        END_ID (inclusive).

        This repository contains a sample .ini file used to configure
        various aspects of the tool. By default it looks for it in the
        root directory under the name 'extract.ini'.
    """
    click.echo('--------------------------------')
    click.echo('Running ABC iDBL Extraction Tool')
    click.echo('--------------------------------')
    click.echo()

    # Get application configuration
    try:
        click.echo('Setting up tool settings...', nl=False)
        settings = get_settings(kwargs)
        click.echo(click.style(' Complete!', fg='green'))
    except exceptions.ImproperlyConfigured:
        click.echo(click.style(' ERROR', fg='red'))

        sys.exit(traceback.format_exc())

    # Setup Sentry error reporting
    click.echo('Setting up Sentry Error reporting...', nl=False)
    sentry_sdk.init(settings['sentry'])
    click.echo(click.style(' Complete!', fg='green'))

    # Setup a request session for the iDBL
    idbl_session = requests.Session()
    idbl_session.headers.update({
        'User-Agent': settings['robot']['user_agent'],
        'From': settings['robot']['from']
    })

    # Setup a request session with the API
    sb_session = requests.Session()

    # Run the extraction process
    start_id = settings['abc_start_id']
    end_id = settings['abc_end_id'] + 1

    with trange(start_id, end_id) as id_range:
        id_range.set_description_str('Extracting iDBL')

        for i in id_range:
            # Apply crawl delay
            time.sleep(settings['crawl_delay'])

            # Extract iDBL data (if applicable)
            try:
                idbl_data = extract_data(i, idbl_session, settings)

            except exceptions.ExtractionError as error:
                # Capture exception, but do not end program
                sentry_sdk.capture_exception(error)

            # Save extracted data
            try:
                print(idbl_data)
                if idbl_data:
                    save_idbl_data(idbl_data, sb_session, settings)
            except exceptions.APIError as error:
                # Capture exception, but do not end program
                sentry_sdk.capture_exception(error)

    # End application
    click.echo()
    click.echo('----------------------------')
    click.echo('ABC iDBL Extraction Complete')
    click.echo('----------------------------')
    sys.exit()

if __name__ == '__main__':
    extract() # pylint: disable=no-value-for-parameter
