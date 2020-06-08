#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells


logger = logging.getLogger()

# Demonstrates that the same graph can be computed twice


def main():

    graph = aiocells.DependencyGraph()

    time = aiocells.Variable()

    # 'aio.timer' will put the current time in the 'time' variable when
    # one second has expired
    timer = functools.partial(aiocells.timer, 1, time)
    printer = aiocells.print_value(time, "variable changed to {value}")

    graph.add_precedence(timer, time)
    graph.add_precedence(time, printer)
    logger.debug("graph: %s", graph)

    logger.info("First computation...")
    asyncio.run(aiocells.async_compute_concurrent(graph))
    logger.debug("graph: %s", graph)

    logger.info("Second computation...")
    asyncio.run(aiocells.async_compute_concurrent(graph))
    logger.debug("graph: %s", graph)
