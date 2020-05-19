#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells.basic as basic
import aiocells.aio as aio
import aiocells.mod as mod
import aiocells.flow as flow


logger = logging.getLogger()


def main():

    clock = mod.Clock()
    graph = basic.DependencyGraph()

    time = mod.ModVariable(clock)
    printer = mod.ModPrinter(clock, time, "variable_1 changed to {value}")
    graph.add_precedence(time, printer)

    timer_0 = functools.partial(aio.timer, 0, time)
    graph.add_precedence(timer_0, time)

    # Flow graphs are generally interested in input values that keep changing
    # over time. Here, we simulate that by setting up a repeating timer. We
    # do that, with the 'flow.repeat' function. This function marks the given
    # function as a 'repeater function', which instructs to'flow.compute_flow'
    # to repeat the function every time it returns. This example will continue
    # until it is interrupted with Ctrl-C.
    repeat_timer = flow.repeat(functools.partial(aio.timer, 1, time))
    graph.add_precedence(repeat_timer, time)

    asyncio.run(flow.compute_flow(graph))
