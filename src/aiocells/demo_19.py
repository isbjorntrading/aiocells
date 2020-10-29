#!/usr/bin/env python3

import asyncio
import functools
import logging

import aiocells


logger = logging.getLogger()


def subgraph(name, period):

    clock = aiocells.ModClock()
    graph = aiocells.DependencyGraph()

    time = aiocells.ModVariable(clock)
    printer = aiocells.ModPrinter(
        clock, time, f"time in \"{name}\" changed to {{value}}"
    )
    graph.add_precedence(time, printer)

    timer_0 = functools.partial(aiocells.timer, 0, time)
    graph.add_precedence(timer_0, time)

    repeat_timer = aiocells.repeat(functools.partial(
        aiocells.timer, period, time
    ))
    graph.add_precedence(repeat_timer, time)

    return graph


async def async_main():

    graph = aiocells.DependencyGraph()

    subgraph_1 = subgraph("graph_1", 0.7)
    subgraph_2 = subgraph("graph_2", 1.5)

    one_step_1 = await aiocells.compute_flow(subgraph_1)
    graph.add_node(aiocells.repeat(one_step_1))

    one_step_2 = await aiocells.compute_flow(subgraph_2)
    graph.add_node(aiocells.repeat(one_step_2))

    print()
    print("Ctrl-C to exit the demo")
    print()

    one_step = await aiocells.compute_flow(graph)

    while (await one_step()):
        pass


def main():
    asyncio.run(async_main())
