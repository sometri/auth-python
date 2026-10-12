import click
from flask.cli import with_appcontext

from .auth import services


@click.command("create-admin")
@click.argument("email")
@click.option("--name", default="Admin", help="Display name.")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Admin password.",
)
@with_appcontext
def create_admin_command(email, name, password):
    """Create an ADMIN user."""
    if services.get_user_by_email(email):
        raise click.ClickException(f"{email} is already registered.")
    if len(password) < 6:
        raise click.ClickException("Password must be at least 6 characters.")
    services.create_user(name, email, password, role="ADMIN")
    click.echo(f"Created admin user: {email}")


def register_cli(app):
    app.cli.add_command(create_admin_command)
