"""An Alberta Blue Cross iDBL extraction tool."""
import click


@click.command()
@click.option(
    '--config', default='extraction.ini', type=click.File(),
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

        Save locations for files can be specified in the .ini file.
    """
    print(kwargs)

if __name__ == '__main__':
    extract() # pylint: disable=no-value-for-parameter
