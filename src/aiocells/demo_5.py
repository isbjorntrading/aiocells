#!/usr/bin/env python3

import asyncio
from functools import partial

import aiocells

# This example demonstrates graph nodes that are coroutines. We use
# a different computer; one that know how to deal with coroutines.


def main():
    graph = aiocells.DependencyGraph()

    # First, we add a lambda function
    before_sleep = graph.add_node(lambda: print("Sleeping..."))

    # Second, we create a coroutine function using functools.partial. This
    # is the closest we can get to a lambda for an async function
    sleep_2 = partial(asyncio.sleep, 2)

    # Finally, another lambda function
    wake_up = graph.add_node(lambda: print("Woke up!"))

    # Here, 'sleep' will implicitly be added to the graph because it is
    # part of the precedence relationship
    graph.add_precedence(before_sleep, sleep_2)
    graph.add_precedence(sleep_2, wake_up)

    # Here, we use the `async_compute_sequential`, which, like
    # `compute_sequential`, call the nodes in a topologically correct sequence.
    # However, whereas `compute_sequential` only supports vanilla callables,
    # `async_compute_sequential` additionally supports coroutine functions,
    # as defined by `inspect.iscoroutinefunction`. However, the execution is
    # still sequential. Each coroutine function is executed using 'await' and
    # must complete before the next node is executed. The function
    # `async_compute_sequential` is a coroutine and must be awaited.  Here,
    # we simply pass it to `asyncio.run`.
    asyncio.run(aiocells.async_compute_sequential(graph))
