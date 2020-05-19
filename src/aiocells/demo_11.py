#!/usr/bin/env python3

import asyncio
from functools import partial

import isbjorn.stable.time as time
import aiocells.basic as basic
import aiocells.aio as aio

# Demonstrates adding nodes to a graph which themselves are graph
# computations. Importantly, the subgraphs execute concurrently with
# one another.


async def run_subgraph(name):
    graph = basic.DependencyGraph()
    sleep_2 = partial(asyncio.sleep, 2)
    graph.add_node(sleep_2)
    print(f"Running subgraph {name}")
    await aio.async_compute_concurrent(graph)


def create_graph(stopwatch):

    graph = basic.DependencyGraph()

    start_stopwatch = graph.add_node(stopwatch.start)
    stop_stopwatch = graph.add_node(stopwatch.stop)

    for i in range(10):
        subgraph = graph.add_node(partial(run_subgraph, f"{i}"))
        graph.add_precedence(start_stopwatch, subgraph)
        graph.add_precedence(subgraph, stop_stopwatch)

    return graph


def main():

    stopwatch = time.Stopwatch()
    graph = create_graph(stopwatch)

    asyncio.run(aio.async_compute_concurrent(graph))
    print("Computation with aio.async_compute_concurrent took"
          f" {stopwatch.elapsed_time()}")
