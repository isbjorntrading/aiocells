#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells


logger = logging.getLogger()


async def async_main():

    clock = aiocells.ModClock()
    graph = aiocells.DependencyGraph()

    # Two completely unrelated sequences are added to the graph. They
    # run concurrently.

    time_1 = aiocells.ModVariable(clock)
    timer_1 = aiocells.source(functools.partial(aiocells.timer, 1, time_1))
    assert aiocells.is_source(timer_1)

    printer_1 = aiocells.ModPrinter(clock, time_1, "time_1 changed to {value}")
    graph.add_precedence(timer_1, time_1)
    graph.add_precedence(time_1, printer_1)

    time_3 = aiocells.ModVariable(clock)
    timer_3 = aiocells.source(functools.partial(aiocells.timer, 3, time_3))
    assert aiocells.is_source(timer_3)
    printer_3 = aiocells.ModPrinter(clock, time_3, "time_3 changed to {value}")
    graph.add_precedence(timer_3, time_3)
    graph.add_precedence(time_3, printer_3)

    # With a flow computation, when any of the input nodes returns, all
    # non-input nodes are computed in topological order.  When this happens, we
    # are generally only interested in nodes that change as a result of the
    # input node returning. So, in this case, we see a message from "time_1"
    # every second and a message from "time_3" every 3 seconds

    while await aiocells.compute_flow(graph):
        pass


def main():
    asyncio.run(async_main())
