import asyncio
import collections
import dataclasses
import inspect
import logging

import aiocells.aio as aio
import aiocells.basic as basic

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

    input_tasks: set


async def compute_flow(graph):

    logger.debug("enter, graph.name=%s", graph.name)

    if not hasattr(graph, "__flow_state"):
        logger.debug("First invocation, initialising flow state")
        callables, input_tasks = aio.prepare_ready_set(graph.input_nodes)
        assert len(callables) == 0, "Input nodes must be coroutines in " + \
            f"\"{graph.name}\": {basic.node_names(callables)}"
        graph.__flow_state = FlowState(input_tasks)

    flow_state = graph.__flow_state

    try:
        # This is inside 'try' block so that the 'finally' block is executed
        if len(flow_state.input_tasks) == 0:
            return len(flow_state.input_tasks)

        # Wait for at least one input node to complete
        logger.debug(
            "Waiting for input tasks, input_tasks=%s",
            basic.task_names(flow_state.input_tasks)
        )
        completed_input_tasks, flow_state.input_tasks = await asyncio.wait(
            flow_state.input_tasks,
            return_when=asyncio.FIRST_COMPLETED
        )

        logger.debug("Input received")
        # Here, we create new tasks for any input functions whose current
        # task has completed. For example, for a socket reader task that
        # has read some data and returned, we want to create a new task so
        # that it can read some more data
        aio.raise_task_exceptions(completed_input_tasks)
        completed_input_functions = [
            task.aio_coroutine_function
            for task in completed_input_tasks
        ]
        logger.debug("completed_input_functions: %s",
                     basic.node_names(completed_input_functions))
        callables, new_tasks = aio.prepare_ready_set(
            completed_input_functions
        )
        assert len(callables) == 0, "Input nodes must be coroutines in " + \
            f"\"{graph.name}\": {basic.node_names(callables)}"

        logger.debug("new_tasks: %s", basic.task_names(new_tasks))
        flow_state.input_tasks |= new_tasks

        logger.debug("Computing dependent nodes")
        for node in graph.topological_ordering:
            if node in graph.input_nodes:
                continue
            logger.debug("Computing dependent node: %s", basic.node_name(node))
            if inspect.iscoroutinefunction(node):
                await node()
            else:
                assert callable(node)
                node()

        return len(flow_state.input_tasks)

    except asyncio.CancelledError:
        await aio.cancel_tasks(flow_state.input_tasks)
        flow_state.input_tasks.clear()
        logger.debug("Caught asyncio.CancelledError in %s", graph.name)
        # Don't reraise - this is an expected error when cancelling the
        # flow with `cancel_flow`
    except Exception as e:
        await aio.cancel_tasks(flow_state.input_tasks)
        logger.debug("Caught exception %s in %s", e, graph.name)
        # Reraise - this is an unexpected exception
        raise
    finally:
        logger.debug("exit, graph.name=%s, len(flow_state.input_tasks)=%s",
                     graph.name, len(flow_state.input_tasks))


async def cancel_flow(graph):
    if not hasattr(graph, "__flow_state"):
        raise Exception("Graph does not have __flow_state attribute")
    logger.debug("Cancelling tasks in %s", graph.name)
    await aio.cancel_tasks(graph.__flow_state.input_tasks)
