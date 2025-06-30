import click
from magician.config.interpreter import ConfigInterpreter
from magician.config.parser import parse_config_file
from magician.settings import get_config


@click.command()
@click.argument("schema", type=str)
def main(schema: str):
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
