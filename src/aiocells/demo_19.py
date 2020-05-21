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

    timer_0 = functools.partial(aiocells.timer, 0, time)
    graph.add_precedence(timer_0, time)

    repeat_timer = aiocells.repeat(functools.partial(
        aiocells.timer, period, time
    ))
    graph.add_precedence(repeat_timer, time)

    return graph


def main():

    graph = aiocells.DependencyGraph()

    subgraph_1 = subgraph("graph_1", 0.7)
    subgraph_2 = subgraph("graph_2", 1.5)

    graph.add_node(functools.partial(aiocells.compute_flow, subgraph_1))
    graph.add_node(functools.partial(aiocells.compute_flow, subgraph_2))

    print()
    print("Ctrl-C to exit the demo")
    print()

    asyncio.run(aiocells.compute_flow(graph))
