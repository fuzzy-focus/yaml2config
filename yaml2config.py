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

    The config files will have the same name as the 
    template files without the '.j2' extension.
    '''
    if update_templates:
        _update_templates_repo(template_dir)
    config_data = _load_yaml(yaml_file)
    no_errors = True
    if isinstance(config_data['template'], list):
        templates = config_data['template'] 
    else:
        templates = [config_data['template']]
    for template_file in templates:
        try: 
            _write_template(config_data, template_dir, template_file, out_dir)
        except WriteConfigError as e:
            no_errors = False
    if no_errors:
        sys.exit(0)
    else:
        sys.exit(1)


class WriteConfigError(RuntimeError):
    pass


def _load_yaml(yaml_file):
    '''load yaml file'''
    try:
        config_data = yaml.load(yaml_file)
    except yaml.YAMLError as e:
        click.echo(click.style('Error in config file:' + str(template_dir), fg='red')
                                + '\n' + repr(e), err=True)
        sys.exit(1)
    return config_data


def _load_template(template_dir, template_file):
    '''load jinja template'''
    try:
        env = Environment(loader = FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(template_file)
    except TemplateError as e:
        click.echo(click.style('Error in the template file:' + str(Path(template_dir) / template_file), fg='red')
                                + '\n' + repr(e), err=True)
        raise WriteConfigError()
    return template


def _write_config(config_data, template, out_file):
    '''render and write config'''
    try:
        rendered = template.render(config_data)
    except TemplateError as e:
        click.echo(click.style('Error during rendering:' + str(template_dir), fg='red')
                                + '\n' + repr(e), err=True)
        raise WriteConfigError()
    else:
        with open(out_file, 'w') as f:
            f.write(rendered)
        click.echo('created config file at ' + click.style(str(out_file), fg='yellow'))

def _write_template(config_data, template_dir, template_file, out_dir):
    '''loads config template, renders it and writes it.'''
    template = _load_template(template_dir, template_file)
    out_file = Path(out_dir) / template_file[:-3] #remove .j2 extension
    _write_config(config_data, template, out_file)

def _update_templates_repo(template_dir):
    '''assume template_dir is a git repo, then pull from origin:master'''
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
