import click
import aiocells.demo_1
import aiocells.demo_2

@click.group()
def main():
    pass

@main.command()
def demo_1():
    aiocells.demo_1.main()

@main.command()
def demo_2():
    aiocells.demo_2.main()
