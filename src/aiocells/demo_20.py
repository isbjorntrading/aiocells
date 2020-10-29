#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells


logger = logging.getLogger()


async def async_printer(variable):
    print(f"value: {variable.value}")


async def async_main():

    # Tests an async internal node in a flow graph

    graph = aiocells.DependencyGraph()

    time = aiocells.Variable()
    printer = graph.add_node(functools.partial(async_printer, time))

    graph.add_precedence(time, printer)

    # This example will continue until it is interrupted with Ctrl-C.
    #
    # Note that marking a function to be repeater function currently only
    # affects the behaviour of 'compute_flow' and not any of the other
    # `compute` functions.

    print()
    print("Ctrl-C to exit the demo")
    print()
    repeat_timer = functools.partial(aiocells.timer, 1, time)
    graph.add_precedence(repeat_timer, time)

    while await aiocells.compute_flow(graph):
        pass


def main():
    asyncio.run(async_main())
