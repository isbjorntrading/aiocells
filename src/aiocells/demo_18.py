#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells


logger = logging.getLogger()


def main():

    clock = aiocells.ModClock()
    graph = aiocells.DependencyGraph()

    time = aiocells.ModVariable(clock)
    printer = aiocells.ModPrinter(clock, time, "variable_1 changed to {value}")
    graph.add_precedence(time, printer)

    timer_0 = functools.partial(aiocells.timer, 0, time)
    graph.add_precedence(timer_0, time)

    # Flow graphs are generally interested in input values that keep changing
    # over time. Here, we simulate that by setting up a repeating timer. We do
    # that, with the 'aiocells.repeat' function. This function marks the passed
    # function as a 'repeater function', which instructs
    # 'aiocells.compute_flow' to repeat the function every time it returns.
    # This, the timer will be repeated ad infinitum.
    #
    # This example will continue until it is interrupted with Ctrl-C.
    #
    # Note that marking a function to be repeater function currently only
    # affects the behaviour of 'compute_flow' and not any of the other
    # `compute` functions.

    print()
    print("Ctrl-C to exit the demo")
    print()
    repeat_timer = aiocells.repeat(functools.partial(aiocells.timer, 1, time))
    graph.add_precedence(repeat_timer, time)

    asyncio.run(aiocells.compute_flow(graph))
