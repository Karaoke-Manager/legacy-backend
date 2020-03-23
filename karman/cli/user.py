import sys

import click
from faker import Faker
from flask.cli import AppGroup
from termcolor import colored

from karman.cli.helpers import abort_if_false
from karman.models import db, User

user_command = AppGroup("user")


@user_command.command("create")
@click.argument("name")
@click.option("--no-pw", "password", flag_value="")
@click.option("--admin/--no-admin", default=False)
@click.option("-p", "--password")
@click.password_option("-P", "password")
def create_user(name: str, password: str, admin: bool):
    user: User = User.query.filter_by(username=name).first()
    if user:
        print(colored("User already exists", "red"), file=sys.stderr)
        exit(1)
    if password == "":
        password = Faker().password()
        print("Using generated password: {}".format(password))
    user = User(username=name, password=password, is_admin=admin)
    db.session.add(user)
    db.session.commit()
    print(colored("User Created", "green"))


@user_command.command("delete")
@click.argument("name")
@click.option("-f", "--force", is_flag=True)
@click.option('--yes', is_flag=True, callback=abort_if_false, expose_value=False,
              prompt='This operation cannot be undone. Proceed?')
def delete_user(name: str, force: bool):
    if name == "all":
        User.query.delete()
        db.session.commit()
        print(colored("All users deleted"))
        return
    user: User = User.query.filter_by(username=name).first()
    if not user and not force:
        print(colored("User not found", "red"), file=sys.stderr)
        exit(1)
    elif user:
        db.session.delete(user)
        db.session.commit()
    print(colored("User Deleted", "green"))
