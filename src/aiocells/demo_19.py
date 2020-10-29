#!/usr/bin/env python3

import asyncio
import functools

import aiocells


def subgraph(name, period):

    clock = aiocells.ModClock()
    graph = aiocells.DependencyGraph()

    time = aiocells.ModVariable(clock)
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

    graph = aiocells.DependencyGraph()

    subgraph_1 = subgraph("graph_1", 0.7)
    subgraph_2 = subgraph("graph_2", 1.5)

    graph.add_node(functools.partial(aiocells.compute_flow, subgraph_1))
    graph.add_node(functools.partial(aiocells.compute_flow, subgraph_2))

    print()
    print("Ctrl-C to exit the demo")
    print()

    while await aiocells.compute_flow(graph):
        pass


def main():
    asyncio.run(async_main())
