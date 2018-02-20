from distutils.core import setup
import py2exe


'''
so far untested because py2exe isnt maintained and does not support current python versions.

bummer.
'''

setup(name='yaml2config',
      version='0.1',
      py_modules=['yaml2config'],
      install_requires=[
          'click',
          'PyYAML',
          'Jinja2',
          ],
      entry_points='''
                    [console_scripts]
                    yaml2config=yaml2config:convert_yaml
                   ''',
      console=['yaml2config.py'])
