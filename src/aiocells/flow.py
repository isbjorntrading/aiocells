import asyncio
import inspect

import aiocells.aio as aio

REPEATER = "cells.flow.repeater"


def repeat(function):
    if not inspect.iscoroutinefunction(function):
        raise ValueError("Event source must be a coroutine function")
    setattr(function, REPEATER, True)
    return function


def is_repeater(function):
    return getattr(function, REPEATER, False)


async def compute_flow(graph):
    assert graph is not None
    input_nodes = graph.input_nodes
    callables, running_tasks = aio.prepare_ready_set(input_nodes)
    if len(callables) > 0:
        raise Exception("Input nodes must be coroutines")
    # Wait for at least one input node to complete
    while len(running_tasks) > 0:
        completed_tasks, running_tasks = await asyncio.wait(
            running_tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        aio.raise_task_exceptions(completed_tasks)
        completed_coro_functions = [
            task.aio_coroutine_function
            for task in completed_tasks
            if is_repeater(task.aio_coroutine_function)
        ]
        callables, new_tasks = aio.prepare_ready_set(completed_coro_functions)
        assert len(callables) == 0
        running_tasks |= new_tasks
        for node in graph.topological_ordering:
            if node in input_nodes:
                continue
            if inspect.iscoroutinefunction(node):
                raise Exception("Cannot handle async internal nodes yet")
            assert callable(node)
            node()
