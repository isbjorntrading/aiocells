#!/usr/bin/env python3

import asyncio

import isbjorn.stable.time as time
import isbjorn.incubator.cells.aio as aio
import isbjorn.incubator.cells.demo_6 as demo_6


def main():
    stopwatch = time.Stopwatch()
    graph = demo_6.create_graph(stopwatch)

    # Here, we run the same graph as the previous demo but we use
    # 'async_compute_concurrent' which will run the two sleeps concurrently.
    # Thus, the execution time will be around 2 seconds, the maximum of
    # the two sleeps.
    asyncio.run(aio.async_compute_concurrent(graph))
    print("Computation with aio.async_compute_concurrent took"
          f" {stopwatch.elapsed_time()}")
