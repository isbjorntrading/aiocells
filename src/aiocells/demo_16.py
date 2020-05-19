#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells


logger = logging.getLogger()


def main():

    clock = aiocells.ModClock()
    graph = aiocells.DependencyGraph()

    # Three completely unrelated sequences are added to the graph. They
    # run concurrently.
    time_0 = aiocells.ModVariable(clock)
    timer_0 = functools.partial(aiocells.timer, 0, time_0)
    printer_0 = aiocells.ModPrinter(clock, time_0, "time_0 changed to {value}")
    graph.add_precedence(timer_0, time_0)
    graph.add_precedence(time_0, printer_0)

    time_1 = aiocells.ModVariable(clock)
    timer_1 = functools.partial(aiocells.timer, 1, time_1)
    printer_1 = aiocells.ModPrinter(clock, time_1, "time_1 changed to {value}")
    graph.add_precedence(timer_1, time_1)
    graph.add_precedence(time_1, printer_1)

    time_3 = aiocells.ModVariable(clock)
    timer_3 = functools.partial(aiocells.timer, 3, time_3)
    printer_3 = aiocells.ModPrinter(clock, time_3, "time_3 changed to {value}")
    graph.add_precedence(timer_3, time_3)
    graph.add_precedence(time_3, printer_3)

    # With a flow computation, only input nodes (those with no dependencies),
    # can be coroutine functions. When any one of those nodes returns, the
    # graph is computed. When this happens, we are generally only interested
    # in nodes that change as a result of the input node returning. So, in
    # this case, we see a message at 0 seconds, 1 second and 3 seconds.
    asyncio.run(aiocells.compute_flow(graph))
