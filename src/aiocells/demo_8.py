#!/usr/bin/env python3

import asyncio
import time

import aiocells


def create_graph(stopwatch):
    graph = aiocells.DependencyGraph()

    start_stopwatch = stopwatch.start

    # Note that these two sleeps are just lambdas. They are vanilla
    # callables and not coroutine functions. Thus, they cannot be run
    # concurrently. Thus, the total run time will be about 3 seconds even
    # if we use the concurrent computer.
    sleep_1 = graph.add_node(lambda: time.sleep(1))
    sleep_2 = graph.add_node(lambda: time.sleep(2))

    stop_stopwatch = stopwatch.stop

    graph.add_precedence(start_stopwatch, sleep_1)
    graph.add_precedence(sleep_1, stop_stopwatch)

    graph.add_precedence(start_stopwatch, sleep_2)
    graph.add_precedence(sleep_2, stop_stopwatch)

    return graph


def main():

    stopwatch = aiocells.Stopwatch()
    graph = create_graph(stopwatch)

    print("Should take about 3 seconds...")
    asyncio.run(aiocells.async_compute_concurrent_simple(graph))
    print("Computation with `async_compute_concurrent_simple` took "
          f"{stopwatch.elapsed_time()}")

    print("Should take about 3 seconds...")
    asyncio.run(aiocells.async_compute_concurrent(graph))
    print("Computation with `async_compute_concurrent` took "
          f"{stopwatch.elapsed_time()}")
