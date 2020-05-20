#!/usr/bin/env python3

import asyncio

import aiocells


def create_graph(stopwatch):

    graph = aiocells.DependencyGraph()

    start_stopwatch = stopwatch.start
    stop_stopwatch = stopwatch.stop

    for t in range(100000):
        def null():
            pass
        graph.add_precedence(start_stopwatch, null)
        graph.add_precedence(null, stop_stopwatch)

    return graph


def main():

    stopwatch = aiocells.Stopwatch()
    graph = create_graph(stopwatch)

    # How long does it take to compute 100000 null callables with
    # async_compute_concurrent_simple?
    asyncio.run(aiocells.async_compute_concurrent_simple(graph))
    print("Computation with async_compute_concurrent_simple took"
          f"{stopwatch.elapsed_time()}")

    # How long does it take to compute 100000 null callables with
    # async_compute_concurrent?
    asyncio.run(aiocells.async_compute_concurrent(graph))
    print("Computation with async_compute_concurrent took"
          f" {stopwatch.elapsed_time()}")
