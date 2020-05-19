#!/usr/bin/env python3

import asyncio

import aiocells
import aiocells.demo_6 as demo_6


def main():
    stopwatch = aiocells.Stopwatch()
    graph = demo_6.create_graph(stopwatch)

    # Here, we run the same graph as the previous demo but we use
    # 'async_compute_concurrent' which will run the two sleeps concurrently.
    # Thus, the execution time will be around 2 seconds, the maximum of
    # the two sleeps.

    print("Running previous demo's graph concurrently.")
    print("Total execution time should be about 2 seconds...")
    asyncio.run(aiocells.async_compute_concurrent(graph))
    print("Computation with `async_compute_concurrent` took"
          f" {stopwatch.elapsed_time()}")
