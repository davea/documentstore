import yaml
import os

"""
Imports keys/values from 'config.yml' into module-level scope.

This module can then be imported by the django settings module.
"""

yml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config.yml"))

if not os.path.isfile(yml_path):
    raise Exception("Couldn't find '{}'".format(yml_path))

try:
    with open(yml_path, 'rb') as f:
        locals().update(yaml.load(f.read()))
except:
    raise Exception("Couldn't read/parse '{}'".format(yml_path))
