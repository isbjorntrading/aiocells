import collections
import copy
import datetime
import enum
import functools
import inspect
import logging


SOURCE = "__aiocells_source__"


def source(function):
    if not inspect.iscoroutinefunction(function):
        raise ValueError("Event source must be a coroutine "
                         f"function: {function=}")
    setattr(function, SOURCE, True)
    return function


def is_source(function):
    return getattr(function, SOURCE, False)


class Stopwatch:

    def __init__(
        self,
        stop_message=None,
        writer=print,
        now_function=datetime.datetime.utcnow
    ):
        self.__now = now_function
        self.__is_running = False
        self.__start_time = None
        self.__lap_start_time = None
        self.__stop_message = stop_message
        self.__writer = writer

    @property
    def is_running(self):
        return self.__is_running

    def start(self):
        assert not self.__is_running
        self.__start_time = self.now()
        self.__lap_start_time = self.__start_time
        self.__is_running = True

    def stop(self):
        assert self.__is_running
        self.__stop_time = self.now()
        self.__is_running = False

    def restart(self):
        self.stop()
        self.start()

    def elapsed_time(self, return_lap_time=False):
        elapsed_time_result = None
        lap_time_result = None
        if self.__start_time is None:
            elapsed_time_result = None
            lap_time_result = None
        elif self.__is_running:
            now = self.now()
            elapsed_time_result = now - self.__start_time
            lap_time_result = now - self.__lap_start_time
            if return_lap_time:
                self.__lap_start_time = now
        else:
            elapsed_time_result = self.__stop_time - self.__start_time
            lap_time_result = self.__stop_time - self.__lap_start_time

        if return_lap_time:
            return (elapsed_time_result, lap_time_result)
        else:
            return elapsed_time_result

    def now(self):
        return self.__now()

    # Context manager methods

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.stop()
        if self.__stop_message and not traceback:
            self.__writer(self.__stop_message.format(
                elapsed_time=self.elapsed_time()
            ))
        if traceback:
            return False
        return True


class Variable:

    def __init__(self, *, value=None, name=None):
        self.name = name
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __call__(self):
        pass

    def __str__(self):
        if self.name is None:
            return repr(self)
        return self.name


def print_value(input_cell, message):
    def f():
        print(message.format(value=input_cell.value))
    return f


def arg_getter(arg):

    # If the arg is an object with a "value" attribute, we return a function
    # that will return the value when called.
    if hasattr(arg, "value"):
        def value_getter():
            return arg.value
        return value_getter

    # If the arg is a sequence, we first generate a list of getters for
    # the elements of the list. When then return a function that invokes
    # those getters when it is invoked.
    if isinstance(arg, (list, tuple)):
        # Here's the list of getters for the sequence elements
        getters = [arg_getter(x) for x in arg]

        # Here's the function that will invoke those getters when it is
        # invoked
        def sequence_getter():
            return type(arg)(g() for g in getters)
        return sequence_getter

    if not isinstance(arg, str) and \
       isinstance(arg, collections.abc.Collection):
        raise Exception(f"Don't know what to do with arg of type {type(arg)}")

    # Arg is neither an object with a "value" attribute and nor is it a
    # collection or a map. In this case, we consider the value to be a literal.
    # We generate a function that simply returns the value as is
    def literal_getter():
        return arg
    return literal_getter


def assign(destination, function, *arguments):
    """Call a function with given argument nodes and assign the result
    to a destination variable.

    Args:
        - destination   - a node implementing the 'Variable' interface
        - function      - a callable or a coroutine function
        - arguments     - nodes to supply the arguments to the function

    Returns:
        - depending on the type of the 'function' argument, a callable or
          a coroutine function
    """
    getters = [arg_getter(argument) for argument in arguments]

    if inspect.iscoroutinefunction(function):
        async def assigner():
            args = [getter() for getter in getters]
            destination.value = await function(*args)
        return assigner

    else:
        def assigner():
            args = [getter() for getter in getters]
            destination.value = function(*args)
        return assigner


class GraphException(Exception):

    def __init__(self, message):
        super(GraphException, self).__init__(message)


class CircularDependency(GraphException):

    def __init__(self, message="Circular dependency detected in graph"):
        super(CircularDependency, self).__init__(message)

# The following function implements Tarjan's algorthim for topological sort,
# which I got from the web. I don't know where exactly.
#
# Algorithm:
#
# L = Empty list that will contain the sorted nodes
# while there are unmarked nodes do
#   select an unmarked node n
#   visit(n)
#
# function visit(node n)
#    if n has a temporary mark then stop (not a DAG)
#    if n is not marked (i.e. has not been visited yet) then
#       mark n temporarily
#       for each node m with an edge from n to m do
#           visit(m)
#       unmark n temporarily
#       mark n permanently
#       add n to head of L
#


def topological_sort(dependency_dict: dict):
    """ 'dependency_dict' is a dict describing dependencies between nodes.
    There must be a key for each node in the graph and the value is a list of
    nodes on which the key is dependent. If a node is present in a dependency
    list but has not dependency list of its own, it is assumed to have no
    dependencies.

    Args:
        . dependency_dict
    """

    # Extract list of nodes from dependency_dict
    nodes = set(dependency_dict.keys()).union(*dependency_dict.values())

    ordering = []

    class Mark(enum.Enum):

        NONE = 1
        TEMPORARY = 2
        MARKED = 3

    marks = {node: Mark.NONE for node in nodes}

    def visit_node(node):
        mark = marks[node]
        if mark == Mark.TEMPORARY:
            raise CircularDependency()
        assert mark == Mark.NONE or mark == Mark.MARKED
        if mark == Mark.MARKED:
            return
        assert mark == Mark.NONE
        marks[node] = Mark.TEMPORARY
        for dependency in dependency_dict.get(node, []):
            visit_node(dependency)

        marks[node] = Mark.MARKED
        ordering.append(node)

    for node in nodes:
        visit_node(node)

    return ordering


class DependencyGraph:

    def __init__(self, initial_dependencies={}):
        self._topological_ordering = None
        self._precedence_dict = None
        self._input_nodes = None
        self._source_nodes = None
        self.dependency_dict = {}
        for node, dependencies in initial_dependencies.items():
            self.add_node(node)
            for dependency in dependencies:
                self.add_dependency(node, dependency)

    def __len__(self):
        return len(self.dependency_dict)

    def __str__(self):
        return str(self.dependency_dict)

    def _dirty(self):
        self._topological_ordering = None
        self._precedence_dict = None
        self._input_nodes = None
        self._source_nodes = None

    def add_dependency(self, from_cell, to_cell):
        """Declare a dependency between two nodes. The nodes are implicitly
        added to the graph if they are not yet in it.
        """
        if from_cell is None:
            raise ValueError(f"Invalid argument: from_cell={from_cell}")
        if to_cell is None:
            raise ValueError(f"Invalid argument: to_cell={to_cell}")
        self.add_node(from_cell)
        self.add_node(to_cell)
        if to_cell in self.dependency_dict[from_cell]:
            return
        self._dirty()
        self.dependency_dict[from_cell].add(to_cell)

    def add_precedence(self, from_cell, to_cell):
        self.add_dependency(to_cell, from_cell)

    def add_node(self, node):
        """This function adds a node to the graph without specifying a
        dependency.
        """
        if node is None:
            raise ValueError(f"Invalid argument: node={node}")
        if node in self.dependency_dict:
            return node
        self.dependency_dict[node] = set()
        self._dirty()
        return node

    @property
    def topological_ordering(self):
        if self._topological_ordering is None:
            self._topological_ordering = topological_sort(self.dependency_dict)
        return self._topological_ordering

    def check_for_cycles(self):
        # This has the side-effect of checking for cycles. Also, it is only
        # checked if the graph has been modified since the last time
        # topological_ordering was called.
        self.topological_ordering

    @property
    def precedence_dict(self):
        if self._precedence_dict is None:
            self._precedence_dict = {}
            for dependent, dependencies in self.dependency_dict.items():
                if dependent not in self._precedence_dict:
                    self._precedence_dict[dependent] = set()
                for dependency in dependencies:
                    if dependency not in self._precedence_dict:
                        self._precedence_dict[dependency] = set()
                    self._precedence_dict[dependency].add(dependent)
        return self._precedence_dict

    @property
    def has_cycle(self):
        try:
            self.topological_ordering
            return False
        except GraphException:
            return True

    @property
    def input_nodes(self):
        if self._input_nodes is None:
            self._input_nodes = {
                node for node, dependencies in self.dependency_dict.items()
                if len(dependencies) == 0
            }
        return self._input_nodes

    @property
    def source_nodes(self):
        if self._source_nodes is None:
            self._source_nodes = {
                node for node, dependencies in self.dependency_dict.items()
                if is_source(node)
            }
        return self._source_nodes

    def decorate(self, decorator_factory):
        """This function replaces nodes in the graph with asyncio.Tasks.
        """
        decorators = {}

        def decorated(node):
            decorator = decorators.get(node, None)
            if decorator is None:
                decorator = decorator_factory(node)
                decorators[node] = decorator
            return decorator

        decorated_graph = DependencyGraph()
        for node in self.dependency_dict.keys():
            decorated_node = decorated_graph.add_node(decorated(node))
            for dependency in self.dependency_dict[node]:
                decorated_dependency = decorated(dependency)
                decorated_graph.add_dependency(decorated_node,
                                               decorated_dependency)
        return decorated_graph


def compute_sequential(graph):
    for node in graph.topological_ordering:
        node()


class TopologicalQueue:
    """TopologicalQueue is used by the `aio` package to implement concurrent
    graph computation.

    The method `ready_set` returns all nodes that have no incomplete
    dependencies.

    The method `completed` indicates that a node is complete. This will
    result in `ready_set` changing. The newly completed node will be removed
    and, potentially, some new node will become ready if that node was
    their last remaining incomplete dependency. For convenience, this method
    returns the `now ready set`, which is the set of nodes that were _not_
    ready before this method was called but have now _become_ ready as a
    result of this call.

    `empty` is used to test whether there are any remaining nodes in the
    queue.

    This class is based on functools.TopologicalSorter that will be included
    in Python 3.9. However, it is desiged to work specifically with
    `DependencyGraph` in this module rather than being general.
    """

    def __init__(self, dependency_graph):
        if dependency_graph.has_cycle:
            raise CircularDependency()

        self.dependency_graph = dependency_graph

        # To determine whether a node is read or not, we keep a dict that
        # contains the count of incomplete dependencies for each node. Once
        # that count is zero, the node is ready
        self.dependency_count = {
            node: len(dependencies)
            for node, dependencies in dependency_graph.dependency_dict.items()
        }

        # The ready set is the set of all nodes with no incomplete dependencies
        self.ready = {node for node, dependency_count in
                      self.dependency_count.items() if dependency_count == 0}

        # Note that a node is left in self.dependency_count even if its
        # dependency_count is 0. It will only be removed when it is completed.

    def __len__(self):
        return len(self.dependency_count)

    def empty(self):
        return len(self.dependency_count) == 0

    def ready_set(self):
        return set(self.ready)

    def completed(self, node):
        # Remove node from ready set
        self.ready.remove(node)

        now_ready = set()
        # Remove node from each of its dependents
        dependents = self.dependency_graph.precedence_dict[node]
        for dependent in dependents:
            self.dependency_count[dependent] -= 1
            if self.dependency_count[dependent] == 0:
                # If the dependent now has no incomplete dependencies, it is
                # ready
                self.ready.add(dependent)
                now_ready.add(dependent)
                # As mentioned in the constructor, a node is left in
                # self.dependency_count even if its dependency_count is 0. It
                # will only be removed when it is completed.

        # The node is complete and is removed from dependency_count.
        # When dependency_count is empty, the queue is also empty.
        del self.dependency_count[node]

        return now_ready
