#!/usr/bin/env python3

import asyncio
from functools import partial

import isbjorn.stable.time as time
import aiocells.basic as basic
import aiocells.aio as aio


def create_graph(stopwatch):

    graph = basic.DependencyGraph()

    start_stopwatch = stopwatch.start
    stop_stopwatch = stopwatch.stop

    for t in range(100000):
        sleep_1 = partial(asyncio.sleep, 1)
        graph.add_precedence(start_stopwatch, sleep_1)
        graph.add_precedence(sleep_1, stop_stopwatch)

    return graph


def main():

    stopwatch = time.Stopwatch()
    graph = create_graph(stopwatch)

    # How long does it take to run 100000 async 1 second sleeps with
    # async_compute_concurrent_simple?
    asyncio.run(aio.async_compute_concurrent_simple(graph))
    print("Computation with aio.async_compute_concurrent_simple took"
          f" {stopwatch.elapsed_time()}")

    # How long does it take to run 100000 async 1 second sleeps with
    # async_compute_concurrent?
    asyncio.run(aio.async_compute_concurrent(graph))
    print("Computation with aio.async_compute_concurrent took"
          f" {stopwatch.elapsed_time()}")
