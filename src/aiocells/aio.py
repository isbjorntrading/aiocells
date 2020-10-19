import asyncio
import datetime
import inspect
import logging
import random

from .basic import TopologicalQueue


logger = logging.getLogger()


async def async_compute_sequential(graph):
    for node in graph.topological_ordering:
        assert callable(node) or inspect.iscoroutinefunction(node), f"{node=}"
        if inspect.iscoroutinefunction(node):
            await node()
        else:
            assert callable(node)
            node()


def async_callable(the_callable):
    assert callable(the_callable)

    async def the_async_version():
        return the_callable()
    return the_async_version


def ensure_coroutine(node):
    assert callable(node) or inspect.iscoroutinefunction(node)
    if not inspect.iscoroutinefunction(node):
        node = async_callable(node)
    assert inspect.iscoroutinefunction(node)
    return node()


def create_tasks(nodes):
    return {asyncio.create_task(node) for node in nodes}


class MultipleTaskExceptions:

    def __init__(self, exceptions):
        self.exceptions = exceptions

    def __str__(self):
        return "MultiplTaskExceptions"


def raise_task_exceptions(tasks):
    all_exceptions = [task.exception() for task in tasks if
                      task.exception() is not None]
    if not all_exceptions:
        return
    raise Exception(f"There are {len(all_exceptions)} task exceptions.") \
        from all_exceptions[0]


async def async_compute_concurrent_simple(graph):

    assert graph is not None

    task_graph = graph.decorate(ensure_coroutine)

    queue = TopologicalQueue(task_graph)

    ready_tasks = create_tasks(queue.ready_set())

    while len(ready_tasks):
        assert not queue.empty()
        # 'pending' could be replaced with 'ready_tasks' here
        # and the line after (ready_tasks -= completed) could be removed
        completed, pending = await asyncio.wait(
            ready_tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        raise_task_exceptions(completed)
        ready_tasks -= completed
        for completed_task in completed:
            now_ready = queue.completed(completed_task.get_coro())
            # print(f"now_ready: {now_ready}")
            ready_tasks |= create_tasks(now_ready)
            # print(f"ready_tasks: {ready_tasks}")

    assert len(ready_tasks) == 0
    assert queue.empty(), f"queue.dependency_dict: {queue.dependency_dict}"


def prepare_ready_set(ready_set):
    callables = set()
    tasks = set()
    for f in ready_set:
        if inspect.iscoroutinefunction(f):
            # Generate a coroutine and task for each coro function
            task = asyncio.create_task(f())
            tasks.add(task)
            # Once the task is done, we need to mark the coro function
            # completed in the graph. To do that, we attach the coro function
            # to the task
            task.aio_coroutine_function = f
        elif callable(f):
            callables.add(f)
        else:
            raise ValueError(f"Node is neither a callable nor a"
                             " coro_function: {f}")
    return callables, tasks


async def async_compute_concurrent(graph):
    assert graph is not None

    queue = TopologicalQueue(graph)
    ready_set = queue.ready_set()

    logger.debug("ready_set: %s", ready_set)
    callables, running_tasks = prepare_ready_set(ready_set)

    while not queue.empty():

        while len(callables):
            the_callable = callables.pop()
            the_callable()
            now_ready = queue.completed(the_callable)
            new_callables, new_tasks = prepare_ready_set(now_ready)
            callables |= new_callables
            running_tasks |= new_tasks

        while len(running_tasks) and len(callables) == 0:
            completed_tasks, running_tasks = await asyncio.wait(
                running_tasks,
                return_when=asyncio.FIRST_COMPLETED
            )
            raise_task_exceptions(completed_tasks)
            for completed_task in completed_tasks:
                completed_coro_function = completed_task.aio_coroutine_function
                now_ready = queue.completed(completed_coro_function)
                new_callables, new_tasks = prepare_ready_set(now_ready)
                callables |= new_callables
                running_tasks |= new_tasks

    assert len(running_tasks) == 0
    assert queue.empty()


async def timer(seconds, result_variable):
    await asyncio.sleep(seconds)
    result_variable.value = datetime.datetime.now()


async def cancel_tasks(tasks):
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
