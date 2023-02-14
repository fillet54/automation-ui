import click

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")

@cli.command()
@click.option('--port', default=8056)
def runserver(port):
    import waitress
    from .api.http.server import app

    waitress.serve(app, port=port)

if __name__ == '__main__':
    cli()