#!/usr/bin/env python3

import asyncio
from functools import partial

import isbjorn.stable.time as time
import isbjorn.incubator.cells.basic as basic
import isbjorn.incubator.cells.aio as aio


def create_graph(stopwatch):

    graph = basic.DependencyGraph()

    # The method to start the stopwatch
    start_stopwatch = stopwatch.start

    # Two sleeps. Note that they are asyncio.sleep
    sleep_1 = partial(asyncio.sleep, 1)
    sleep_2 = partial(asyncio.sleep, 2)

    # The method to stop the stopwatch
    stop_stopwatch = stopwatch.stop

    # Start the stopwatch before the first sleep
    graph.add_precedence(start_stopwatch, sleep_1)
    # Stop the stopwatch after the first sleep
    graph.add_precedence(sleep_1, stop_stopwatch)

    # Start the stopwatch before the second sleep
    graph.add_precedence(start_stopwatch, sleep_2)
    # Stop the stopwatch after the second sleep
    graph.add_precedence(sleep_2, stop_stopwatch)

    # Note that there is no precedence relationship between the two
    # sleeps.
    return graph


def main():

    stopwatch = time.Stopwatch()
    graph = create_graph(stopwatch)
    # Even though the graph is a diamond (the sleeps do no depend on each
    # other and _could_ be executed concurrenty, async_compute_sequential
    # does not support concurrent execution. Thus, the execution time is
    # about 3 seconds, the sum of the two sleeps.
    print("Two async sleeps computed sequentially...")
    asyncio.run(aio.async_compute_sequential(graph))
    print("Computation with aio.async_compute_sequential took"
          f" {stopwatch.elapsed_time()}")
