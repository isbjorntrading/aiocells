#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells


logger = logging.getLogger()


async def async_main(iterations=None):

    iterations = iterations if iterations is not None else 10

    clock = aiocells.ModClock()
    graph = aiocells.DependencyGraph(name="demo_1")

    # Two completely unrelated sequences are added to the graph. They
    # run concurrently.

    time_1 = aiocells.ModPlace(clock)
    timer_1 = functools.partial(aiocells.timer, 1, time_1)
    printer_1 = aiocells.ModPrinter(clock, time_1, "time_1 changed to {value}")
    graph.add_precedence(timer_1, time_1)
    graph.add_precedence(time_1, printer_1)

    time_3 = aiocells.ModPlace(clock)
    timer_3 = functools.partial(aiocells.timer, 3, time_3)
    printer_3 = aiocells.ModPrinter(clock, time_3, "time_3 changed to {value}")
    graph.add_precedence(timer_3, time_3)
    graph.add_precedence(time_3, printer_3)

    # With a flow computation, when any of the input nodes returns, all
    # non-input nodes are computed in topological order.  When this happens, we
    # are generally only interested in nodes that change as a result of the
    # input node returning. So, in this case, we see a message from "time_1"
    # every second and a message from "time_3" every 3 seconds

    print()
    print("Demo will complete in 10 iterations. Ctrl-C to cancel.")
    print()

    iteration_count = 0
    while await aiocells.compute_flow(graph):
        iteration_count += 1
        if iteration_count > iterations:
            await aiocells.cancel_flow(graph)


def main(iterations):
    asyncio.run(async_main(iterations))
