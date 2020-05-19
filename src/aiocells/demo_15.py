#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells


logger = logging.getLogger()


# See demo_18 for different way to do this
def main():

    clock = aiocells.ModClock()
    graph = aiocells.DependencyGraph()

    time = aiocells.ModVariable(clock)
    timer = functools.partial(aiocells.timer, 1, time)
    printer = aiocells.ModPrinter(clock, time, "time changed to {value}")

    graph.add_precedence(timer, time)
    graph.add_precedence(time, printer)

    # Demonstrating repeated computation of the same graph. However, 'flow
    # graphs', shown in the next demo, are better suited to this.
    for i in range(10):
        logger.info("Computation %s", i)
        asyncio.run(aiocells.async_compute_concurrent(graph))
