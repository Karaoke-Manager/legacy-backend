from click.testing import Result
from flask.testing import FlaskCliRunner

from karman.cli import user_command
from karman.models import User
from tests.data import SingleUserDataset, UNUSED_USERNAME, MultiUserDataset


def test_create_user_with_password(cli: FlaskCliRunner):
    result: Result = cli.invoke(user_command, ['create', UNUSED_USERNAME, '-p', 'password'])
    user: User = User.query.filter_by(username=UNUSED_USERNAME).first()
    assert user is not None
    assert user.validate_password('password')
    assert 'User Created' in result.output


def test_create_user_without_password(cli: FlaskCliRunner):
    result: Result = cli.invoke(user_command, ['create', UNUSED_USERNAME, '--no-pw'])
    assert User.query.filter_by(username=UNUSED_USERNAME).count() == 1
    assert 'Using generated password:' in result.output
    assert 'User Created' in result.output


def test_create_existing_user(cli: FlaskCliRunner, single_user_dataset: SingleUserDataset):
    data = single_user_dataset
    result: Result = cli.invoke(user_command, ['create', data.user.username, '--no-pw'])
    assert data.user_exists()
    assert result.exit_code == 1
    assert "User already exists" in result.output


def test_delete_user(cli: FlaskCliRunner, single_user_dataset: SingleUserDataset):
    data = single_user_dataset
    result: Result = cli.invoke(user_command, ['delete', data.user.username, "--yes"])
    assert not data.user_exists()
    assert "User Deleted" in result.output


def test_delete_absent_user(cli: FlaskCliRunner):
    result: Result = cli.invoke(user_command, ['delete', UNUSED_USERNAME, "--yes"])
    assert result.exit_code == 1
    assert "User not found" in result.output


def test_force_delete_absent_user(cli: FlaskCliRunner):
    result: Result = cli.invoke(user_command, ['delete', UNUSED_USERNAME, "-f", "--yes"])
    assert result.exit_code == 0
    assert "User Deleted" in result.output


def test_delete_all_users(cli: FlaskCliRunner, multi_user_dataset: MultiUserDataset):
    data = multi_user_dataset
    result: Result = cli.invoke(user_command, ['delete', "all", "--yes"])
    assert data.user_count() == 0
    assert result.exit_code == 0
    print(result.output)
    assert "All users deleted" in result.output
