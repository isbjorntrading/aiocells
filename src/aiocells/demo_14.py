#!/usr/bin/env python3

import asyncio
import datetime
import functools
import logging

import aiocells


logger = logging.getLogger()


# Demonstrates a node where the function is actually a coroutine method.
# In this case, functools.partial must be used to bind the function and
# the object.

class TimerObject:

    def __init__(self, result_variable):
        self.result_variable = result_variable

    async def compute(self):
        logger.debug("sleeping")
        await asyncio.sleep(1)
        logger.debug("woke up")
        self.result_variable.value = datetime.datetime.now()


def main():

    graph = aiocells.DependencyGraph()

    time = aiocells.Variable()
    timer = TimerObject(time)

    # Here, we bind the coroutine method with the object
    compute_timer = functools.partial(TimerObject.compute, timer)
    printer = aiocells.print_value(time, "variable changed to {value}")

    graph.add_precedence(compute_timer, time)
    graph.add_precedence(time, printer)
    logger.debug("graph: %s", graph)

    logger.info("First computation...")
    asyncio.run(aiocells.async_compute_concurrent(graph))
    logger.debug("graph: %s", graph)

    logger.info("Second computation...")
    asyncio.run(aiocells.async_compute_concurrent(graph))
    logger.debug("graph: %s", graph)
