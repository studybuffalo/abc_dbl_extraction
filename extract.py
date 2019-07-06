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
import traceback

import click
import requests
import sentry_sdk
from tqdm import trange

from modules.configuration import Configuration
from modules.exceptions import ImproperlyConfigured
from modules.extraction import extract_data


@click.command()
@click.argument('start-id', type=click.INT)
@click.argument('end-id', type=click.INT)
@click.option(
    '--config', default='extraction.ini', type=click.Path(exists=True),
    help='Path to the .ini config file.'
)
@click.option(
    '--disable-data-upload', is_flag=True, help='Disables "data" API upload.'
)
@click.option(
    '--disable-sub-upload', is_flag=True, help='Disables "sub" API upload.'
)
@click.option(
    '--save-url', is_flag=True, help='Save extracted URLs to file.'
)
@click.option(
    '--save-html', is_flag=True, help='Save extracted HTML data to file.'
)
@click.option(
    '--save-api', is_flag=True, help='Save API request data to file.'
)
@click.option(
    '--use-url-file', is_flag=True, help='Uses extracted URL file.'
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
    click.echo('Running ABC iDBL Extraction Tool')
    click.echo('--------------------------------')

    # Get application configuration
    try:
        click.echo('Setting up tool configuration...', nl=False)

        configuration = Configuration(kwargs)

        click.echo(click.style(' Complete!', fg='green'))
    except ImproperlyConfigured:
        click.echo(click.style(' ERROR', fg='red'))

        sys.exit(traceback.format_exc())

    # Setup Sentry error reporting
    click.echo('Setting up Sentry Error reporting...', nl=False)

    sentry_sdk.init(configuration.settings['sentry'])

    click.echo(click.style(' Complete!', fg='green'))

    # Setup a request session
    session = requests.Session()
    session.headers.update({
        'User-Agent': configuration.settings['robot']['user_agent'],
        'From': configuration.settings['robot']['from']
    })

    # Run the extraction process
    start_id = configuration.settings['abc_start_id']
    end_id = configuration.settings['abc_end_id'] + 1

    with trange(start_id, end_id) as id_range:
        id_range.set_description_str('Extracting iDBL')

        for i in id_range:
            extract_data(i, session, configuration)

    click.echo('----------------------------')
    click.echo('ABC iDBL Extraction Complete')

if __name__ == '__main__':
    extract() # pylint: disable=no-value-for-parameter
