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

    time = aiocells.Place()
    printer = graph.add_node(functools.partial(async_printer, time))

    graph.add_precedence(time, printer)

    # This example will continue until it is interrupted with Ctrl-C.
    #
    # Note that marking a function to be repeater function currently only
    # affects the behaviour of 'compute_flow' and not any of the other
    # `compute` functions.

    print()
    print("Demo will complete in 10 iterations. Ctrl-C to cancel.")
    print()
    repeat_timer = functools.partial(aiocells.timer, 1, time)
    graph.add_precedence(repeat_timer, time)

    iteration_count = 0
    while await aiocells.compute_flow(graph):
        iteration_count += 1
        if iteration_count > 10:
            await aiocells.cancel_flow(graph)


def main():
    asyncio.run(async_main())
