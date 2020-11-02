import asyncio
import collections
import dataclasses
import inspect
import logging

import aiocells.aio as aio

REPEATER = "cells.flow.repeater"

logger = logging.getLogger(__name__)


def repeat(function):
    if not inspect.iscoroutinefunction(function):
        raise ValueError("Event source must be a coroutine "
                         f"function: {function=}")
    setattr(function, REPEATER, True)
    return function


def is_repeater(function):
    return getattr(function, REPEATER, False)


@dataclasses.dataclass
class FlowState:

    callables: list
    running_tasks: list


async def compute_flow(graph):

    logger.debug("enter")

    if not hasattr(graph, "__flow_state"):
        callables, running_tasks = aio.prepare_ready_set(graph.input_nodes)
        graph.__flow_state = FlowState(callables, running_tasks)
        if len(graph.__flow_state.callables) > 0:
            raise Exception(f"Input nodes must be coroutines: {callables=}")

    flow_state = graph.__flow_state

    # Wait for at least one input node to complete
    if len(flow_state.running_tasks) == 0:
        return len(flow_state.running_tasks)

    try:
        logger.debug("Waiting for input tasks")
        completed_tasks, flow_state.running_tasks = await asyncio.wait(
            flow_state.running_tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        logger.debug("Input received")
        aio.raise_task_exceptions(completed_tasks)
        completed_repeater_functions = [
            task.aio_coroutine_function
            for task in completed_tasks
            # if is_repeater(task.aio_coroutine_function)
        ]
        flow_state.callables, new_tasks = aio.prepare_ready_set(
            completed_repeater_functions
        )
        assert len(flow_state.callables) == 0
        flow_state.running_tasks |= new_tasks
        logger.debug("Computing dependent nodes")
        for node in graph.topological_ordering:
            if node in graph.input_nodes:
                continue
            logger.debug("Computing dependent node: %s", node)
            if inspect.iscoroutinefunction(node):
                await node()
            else:
                assert callable(node)
                node()
        return len(flow_state.running_tasks)
    except (asyncio.CancelledError, Exception) as e:
        await aio.cancel_tasks(flow_state.running_tasks)
        raise
