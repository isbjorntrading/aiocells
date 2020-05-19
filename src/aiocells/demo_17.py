#!/usr/bin/env python3

import asyncio
import functools
import logging

import isbjorn.incubator.cells.basic as basic
import isbjorn.incubator.cells.aio as aio
import isbjorn.incubator.cells.mod as mod
import isbjorn.incubator.cells.flow as flow


logger = logging.getLogger()


def main():

    clock = mod.Clock()
    graph = basic.DependencyGraph()

    # Here, we simplify the previous demo by using a single variable to
    # store the time and a single printer to announce the modifications
    # when they happen. Because we are using 'compute_flow', the graph
    # is computed when any of the timers go off.
    time = mod.ModVariable(clock)
    printer = mod.ModPrinter(clock, time, "time changed to {value}")
    graph.add_precedence(time, printer)

    # Set the time after 0 seconds
    timer_0 = functools.partial(aio.timer, 0, time)
    graph.add_precedence(timer_0, time)

    # Set the time after 1 second
    timer_1 = functools.partial(aio.timer, 1, time)
    graph.add_precedence(timer_1, time)

    # Set the time after 3 seconds
    timer_3 = functools.partial(aio.timer, 3, time)
    graph.add_precedence(timer_3, time)

    asyncio.run(flow.compute_flow(graph))
