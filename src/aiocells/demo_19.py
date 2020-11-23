#!/usr/bin/env python3

import asyncio
import functools

import aiocells


def subgraph(name, period):

    clock = aiocells.ModClock()
    graph = aiocells.DependencyGraph(name=name)

    time = aiocells.ModPlace(clock)
    printer = aiocells.ModPrinter(
        clock, time, f"time in \"{name}\" changed to {{value}}"
    )
    graph.add_precedence(time, printer)

    timer = functools.partial(
        aiocells.timer, period, time
    )
    graph.add_precedence(timer, time)

    return graph


async def async_main():

    graph = aiocells.DependencyGraph(name="async_main")

    subgraph_1 = subgraph("graph_1", 0.7)
    subgraph_2 = subgraph("graph_2", 1.5)

    graph.add_node(functools.partial(aiocells.compute_flow, subgraph_1))
    graph.add_node(functools.partial(aiocells.compute_flow, subgraph_2))

    print()
    print("Demo will complete in 10 iterations. Ctrl-C to cancel.")
    print()

    iteration_count = 0
    while await aiocells.compute_flow(graph):
        iteration_count += 1
        if iteration_count > 10:
            await aiocells.cancel_flow(graph)


def main():
    asyncio.run(async_main())
