from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import yaml
import click
import sys

# better jinja exception handling:
# https://github.com/pallets/jinja/blob/master/jinja2/exceptions.py

@click.command()
@click.argument('YAML_file', type=click.File('r'))
@click.option('--out-dir', '-d', type=click.Path(exists=True,writable=True,resolve_path=True),
        default='.', help='write output to this directory (default is current directory)')
def convert_yaml(yaml_file,out_dir):
    '''Generate config file from YAML document

    This script will fill the apropriate Jinja2 Template
    file (specified in the YAML doc) with the parameters
    defined in your YAML file.
    '''


    #Load data from YAML into Python dictionary
    try:
        config_data = yaml.load(yaml_file)
    except yaml.YAMLError as e:
        click.echo('Error in config file:\n', e)
        sys.exit(1)

    #Load Jinja2 template
    try:
        env = Environment(loader = FileSystemLoader('./template'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(config_data['template'])
    except TemplateError as e:
        click.echo('Error in the template file:\n', e)
        sys.exit(1)

    #Render the template with data and click.echo the output
    try:
        rendered = template.render(config_data)
    except TempalteError as e:
        click.echo('Error during rendering:\n', e)
        sys.exit(1)

    out_file = Path(out_dir) / config_data['filename']

    with open(out_file, 'w') as f:
        f.write(rendered)

    click.echo('created config file at ' + str(out_file))
    sys.exit(0)


if __name__ == '__main__':
    convert_yaml()
