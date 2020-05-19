#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells.basic as basic
import aiocells.aio as aio
import aiocells.mod as mod


logger = logging.getLogger()


# See demo_18 for different way to do this
def main():

    clock = mod.Clock()
    graph = basic.DependencyGraph()

    time = mod.ModVariable(clock)
    timer = functools.partial(aio.timer, 1, time)
    printer = mod.ModPrinter(clock, time, "time changed to {value}")

    graph.add_precedence(timer, time)
    graph.add_precedence(time, printer)

    # Demonstrating repeated computation of the same graph. However, 'flow
    # graphs', shown in the next demo, are better suited to this.
    for i in range(10):
        logger.info("Computation %s", i)
        asyncio.run(aio.async_compute_concurrent(graph))
