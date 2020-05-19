`aiocell` is a package that provides tools for synchronous and asynchronous
execution of nodes in a dependency graph.

## Examples

### Hello world

Here is the code for the [first demo](src/aiocells/demo_1.py).

```python
#!/usr/bin/env python3

import aiocells


def hello_world():
    print("Hello, world!")


def main():
    graph = aiocells.DependencyGraph()

    # The node can be any callable, in this case a function.
    graph.add_node(hello_world)
    aiocells.compute_sequential(graph)
```

This is _synchronous_ graph computation. There is only one node in the graph.
It is a function that prints a message. Synchronous nodes must be `callable`.

### Defining ordering constraints

Here is [demo 4](src/aiocells/demo_4.py). It shows how edges between nodes
are defined:


```python
#!/usr/bin/env python3

import time

import aiocells


def main():
    graph = aiocells.DependencyGraph()

    # 'add_node' always returns the node that has just been added, in this
    # case the lambda functions. We will use this below to define precedence
    # relationships
    print_sleeping = graph.add_node(lambda: print("Sleeping..."))
    sleep = graph.add_node(lambda: time.sleep(2))
    print_woke_up = graph.add_node(lambda: print("Woke up!"))

    print("Define the precedence relationships...")
    graph.add_precedence(print_sleeping, sleep)
    graph.add_precedence(sleep, print_woke_up)

    # Now, after we've defined the precedence relationships, we use the
    # simplest computer to compute the graph. The nodes will be called in
    # an order that is consistent with the precedence relationships.
    # Specifically, the nodes are executed in topological order.
    aiocells.compute_sequential(graph)
```

In this case, there are three nodes. After the nodes are added, we define
precedence relationships between them. When the graph is computed, it is
done so in a way that honours the precedence relationships.

### Asynchronous nodes

Below is the code for [demo_5](src/aiocells/demo_5.py). Note the use of
`asyncio.sleep`, `functools.partial` and `aiocells.async_compute_sequential`.

```python
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
```

### Concurrent computation

[demo 6](src/aiocells/demo_6.py) is a an example of graph that _could_ be
computed concurrently but is not due to the use if `async_compute_sequential`.

```python
import asyncio
from functools import partial

import aiocells


def create_graph(stopwatch):

    graph = aiocells.DependencyGraph()

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

    stopwatch = aiocells.Stopwatch()
    graph = create_graph(stopwatch)
    # Even though the graph is a diamond (the sleeps do no depend on each
    # other and _could_ be executed concurrenty, `async_compute_sequential`
    # does not support concurrent execution. Thus, the execution time is
    # about 3 seconds, the sum of the two sleeps.
    print("Two async sleeps computed sequentially.")
    print("Total time should take about 3 seconds...")
    asyncio.run(aiocells.async_compute_sequential(graph))
    print("Computation with `async_compute_sequential` took"
          f" {stopwatch.elapsed_time()}")
```

[demo_7](src/aiocells/demo_7.py) is the same graph as above but computed
concurrently with `async_compute_concurrent`.

```python
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

```

## Installation
