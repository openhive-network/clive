import rich
import typer
from prompt_toolkit.styles import parse_color

from clive import config
from clive.config import settings

app = typer.Typer()


@app.command(name="list")
def list_(name: str = typer.Argument(None, help="Show only the style with the specified name.")) -> None:
    """Show the currently configured style or all styles if no name was given."""
    if name is None:
        rich.print(settings.as_dict()["STYLE"])
        return
    try:
        rich.print(settings.as_dict()["STYLE"][name])
    except KeyError:
        typer.secho(f'Style with name "{name}" was not found.', fg=typer.colors.RED)


@app.command()
def update(
    name: str = typer.Argument(..., help="The name of the style to set."),
    value: str = typer.Argument(..., help="The value of the style to set."),
) -> None:
    """Set a style value."""
    try:
        parse_color(value)
    except ValueError:
        typer.secho(f'"{value}" is not a valid color.', fg=typer.colors.RED)
        return

    config.update("style.toml", {"default": {"style": {name: value}}})
