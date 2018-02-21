from jinja2 import Environment, FileSystemLoader, TemplateError
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
@click.option('--template-dir', '-t', type=click.Path(exists=True,readable=True,resolve_path=True),
        default='./template', help='template search path (default is ./template)')
@click.option('--update-templates', '-u', is_flag=True, help='if template folder is git repo, pull from origin:master')
def convert_yaml(yaml_file, out_dir, template_dir,update_templates=False):
    '''Generate config file from YAML document

    This script will fill the apropriate Jinja2 Template
    file (specified in the YAML doc) with the parameters
    defined in your YAML file.
    '''

    if update_templates:
        update_templates_repo(template_dir)

    #Load data from YAML into Python dictionary
    try:
        config_data = yaml.load(yaml_file)
    except yaml.YAMLError as e:
        click.echo(click.style('Error in config file:' + str(template_dir), fg='red')
                                + '\n' + repr(e), err=True)
        sys.exit(1)

    #Load Jinja2 template
    try:
        env = Environment(loader = FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(config_data['template'])
    except TemplateError as e:
        click.echo(click.style('Error in the template file:' + str(Path(template_dir) / config_data['template']), fg='red')
                                + '\n' + repr(e), err=True)
        sys.exit(1)

    #Render the template with data and click.echo the output
    try:
        rendered = template.render(config_data)
    except TemplateError as e:
        click.echo(click.style('Error during rendering:' + str(template_dir), fg='red')
                                + '\n' + repr(e), err=True)
        sys.exit(1)

    out_file = Path(out_dir) / config_data['filename']

    with open(out_file, 'w') as f:
        f.write(rendered)

    click.echo('created config file at ' + str(out_file))
    sys.exit(0)


def update_templates_repo(template_dir):
    try:
        import git
    except ImportError as e:
        click.echo(click.style('GitPython is not available or not configured.', fg='red') 
                                + '\n' + repr(e), err=True)
        sys.exit(1)
    try:
        repo = git.Repo(template_dir)
        repo.remotes.origin.pull('master')
    except git.exc.GitError as e:
        click.echo(click.style('No valid repository at ' + str(template_dir), fg='red')
                                + '\n' + repr(e), err=True)
        sys.exit(1)
    click.echo('Templates-repository is up to date')



if __name__ == '__main__':
    convert_yaml()
