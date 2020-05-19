#!/usr/bin/env python3

import asyncio
import functools
import logging

import isbjorn.incubator.cells.basic as basic
import isbjorn.incubator.cells.aio as aio


logger = logging.getLogger()

# Demonstrates that the same graph can be computed twice


def main():

    graph = basic.DependencyGraph()

    time = basic.Variable()

    # 'aio.timer' will put the current time in the 'time' variable when
    # one second has expired
    timer = functools.partial(aio.timer, 1, time)
    printer = basic.Printer(time, "  variable changed to {value}")

    graph.add_precedence(timer, time)
    graph.add_precedence(time, printer)
    logger.debug("graph: %s", graph)

    logger.info("First computation...")
    asyncio.run(aio.async_compute_concurrent(graph))
    logger.debug("graph: %s", graph)

    logger.info("Second computation...")
    asyncio.run(aio.async_compute_concurrent(graph))
    logger.debug("graph: %s", graph)
