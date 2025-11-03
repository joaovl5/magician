import pathlib
import click
import shutil
import os
import subprocess
from magician.config.interpreter import ConfigInterpreter
from magician.config.parser import parse_config_file
from magician.settings import get_config


@click.group()
def cli(): ...


@cli.command()
@click.argument(
    "schema",
    type=str,
)
def edit(schema: str):
    """
    Creates new schema based on a template.
    """
    app_cfg = get_config()
    dst_path = app_cfg.schemas_folder / f"{schema}.yml"
    if not dst_path.exists():
        dst_path = app_cfg.schemas_folder / f"{schema}.yaml"
    if not dst_path.exists():
        click.echo(
            click.style(
                f"Schema under the name '{schema}' does not exist in {dst_path}",
                fg="red",
            )
        )
        raise click.Abort()

    editor = os.environ.get("EDITOR", "nano")
    subprocess.call([editor, dst_path.resolve()])


@cli.command()
@click.argument(
    "schema",
    type=str,
)
@click.option(
    "--empty",
    "-e",
    is_flag=True,
    default=False,
    help="Creates empty file without using template.",
)
def new(schema: str, empty: bool = False):
    """
    Creates new schema based on a template.
    """
    app_cfg = get_config()
    dst_path = app_cfg.schemas_folder / f"{schema}.yml"

    if dst_path.exists():
        click.echo(
            click.style(
                f"Schema under the same name already exists in {dst_path}", fg="red"
            )
        )
        raise click.Abort()
    if not empty:
        template_path = app_cfg.examples_folder / "example.yml"
        if not template_path.exists():
            click.echo(
                click.style(
                    f"Template file does not exist in {template_path}", fg="red"
                )
            )
            raise click.Abort()

        shutil.copy(
            src=template_path,
            dst=dst_path,
        )
    else:
        with open(dst_path, "w") as f:
            f.write("")

    editor = os.environ.get("EDITOR", "nano")
    subprocess.call([editor, dst_path.resolve()])


@cli.command()
@click.argument(
    "schema",
    type=str,
)
def remove(schema: str):
    """
    Removes a schema.
    """
    app_cfg = get_config()
    dst_path = app_cfg.schemas_folder.resolve() / f"{schema}.yml"

    if not dst_path.exists():
        dst_path = app_cfg.schemas_folder / f"{schema}.yaml"
    if not dst_path.exists():
        click.echo(
            click.style(f"Schema under the name '{schema}' does not exist.", fg="red")
        )
        raise click.Abort()
    os.remove(path=dst_path.resolve())


@cli.command()
@click.argument(
    "schema",
    type=click.Path(
        exists=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
def save(schema: pathlib.Path):
    """
    Saves local schema file over to the internal schemas folder.
    """
    app_cfg = get_config()
    dst_path = app_cfg.schemas_folder / f"{schema.stem}.yml"

    if dst_path.exists():
        click.echo(
            click.style(
                f"Schema under the same name already exists in {dst_path}", fg="red"
            )
        )
        raise click.Abort()

    shutil.move(
        src=schema,
        dst=dst_path,
    )


@cli.command()
@click.argument("schema", type=str)
def run(schema: str):
    """Run predefined config"""
    app_cfg = get_config()
    schemas_folder = app_cfg.schemas_folder
    schema_path = schemas_folder / f"{schema}.yml"
    if not schema_path.exists():
        schema_path = schemas_folder / f"{schema}.yaml"
    if not schema_path.exists():
        click.echo(
            click.style(
                f"No schema named '{schema}' under the folder {schemas_folder}",
                fg="red",
            ),
            err=True,
        )
        raise click.Abort()

    intr = ConfigInterpreter(app_cfg=app_cfg)
    magic_cfg = parse_config_file(file=schema_path)

    intr.compile(config=magic_cfg, schema_name=schema)
    intr.run(config=magic_cfg, schema_name=schema)
