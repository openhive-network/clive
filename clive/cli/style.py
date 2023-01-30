import rich
import typer

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
