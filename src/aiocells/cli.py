import logging

import click
import klogs

import aiocells.demo_1
import aiocells.demo_2
import aiocells.demo_3
import aiocells.demo_4
import aiocells.demo_5
import aiocells.demo_6
import aiocells.demo_7
import aiocells.demo_8
import aiocells.demo_9
import aiocells.demo_10
import aiocells.demo_11
import aiocells.demo_12
import aiocells.demo_13
import aiocells.demo_14
import aiocells.demo_15
import aiocells.demo_16
import aiocells.demo_17
import aiocells.demo_19
import aiocells.demo_20


@click.group()
@click.option("--log-line-no", default=False)
@click.option("--log-level", type=str, default=logging.INFO)
@click.option("--log-file", type=str, default=None)
def main(log_line_no, log_file, log_level):
    klogs.configure_logging(
        level=log_level,
        with_line_no=log_line_no,
        log_file=log_file,
    )


@main.command()
def demo_1():
    aiocells.demo_1.main()


@main.command()
def demo_2():
    aiocells.demo_2.main()


@main.command()
def demo_3():
    aiocells.demo_3.main()


@main.command()
def demo_4():
    aiocells.demo_4.main()


@main.command()
def demo_5():
    aiocells.demo_5.main()


@main.command()
def demo_6():
    aiocells.demo_6.main()


@main.command()
def demo_7():
    aiocells.demo_7.main()


@main.command()
def demo_8():
    aiocells.demo_8.main()


@main.command()
def demo_9():
    aiocells.demo_9.main()


@main.command()
def demo_10():
    aiocells.demo_10.main()


@main.command()
def demo_11():
    aiocells.demo_11.main()


@main.command()
def demo_12():
    aiocells.demo_12.main()


@main.command()
def demo_13():
    aiocells.demo_13.main()


@main.command()
def demo_14():
    aiocells.demo_14.main()


@main.command()
def demo_15():
    aiocells.demo_15.main()


@main.command()
@click.option("--iterations", type=int)
def demo_16(iterations):
    aiocells.demo_16.main(iterations)


@main.command()
def demo_17():
    aiocells.demo_17.main()


@main.command()
def demo_19():
    aiocells.demo_19.main()


@main.command()
def demo_20():
    aiocells.demo_20.main()
