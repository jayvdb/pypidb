from __future__ import print_function

import sys

import click

from ._db import Database


@click.command()
@click.argument('name')
def cli(name):
    db = Database()
    try:
        url = db.find_project_scm_url(name)
        print(url)
    except Exception as e:
        error_msg = str(e)
        print(error_msg, file=sys.stderr)
