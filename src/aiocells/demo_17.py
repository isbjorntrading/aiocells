#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells


logger = logging.getLogger()


async def async_main():

    clock = aiocells.ModClock()
    graph = aiocells.DependencyGraph()

    # Here, we simplify the previous demo by using a single variable to
    # store the time and a single printer to announce the modifications
    # when they happen. Because we are using 'compute_flow', the graph
    # is computed when any of the timers go off.
    time = aiocells.ModVariable(clock)
    printer = aiocells.ModPrinter(clock, time, "time changed to {value}")
    graph.add_precedence(time, printer)

    # Set the time after 1 second
    timer_1 = functools.partial(aiocells.timer, 1, time)
    graph.add_precedence(timer_1, time)

    # Set the time after 3 seconds
    timer_3 = functools.partial(aiocells.timer, 3, time)
    graph.add_precedence(timer_3, time)

    while await aiocells.compute_flow(graph):
        pass


def main():
    asyncio.run(async_main())
