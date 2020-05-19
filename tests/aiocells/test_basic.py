import operator
import pytest

import isbjorn.incubator.cells.basic as basic


def test_dict():

    d = {"A": set(), "B": {"A"}}
    d2 = dict(d)

    del d2["B"]
    assert "B" in d

# =============================================================================
# Test Variable


def test_cell_setter_and_getter():

    cell_1 = basic.Variable(name="test_cell_1")
    assert cell_1.name == "test_cell_1"
    assert cell_1.value is None

    cell_1.value = 7
    assert cell_1.value == 7

    cell_2 = basic.Variable(name="test_cell_2", value=1)
    assert cell_2.name == "test_cell_2"
    assert cell_2.value == 1

    cell_2.value = -1
    assert cell_2.value == -1

# =============================================================================
# Test Add formula


def test_add_no_inputs():
    output_cell = basic.Variable()

    add = basic.Adder([], output_cell)
    add()

    assert output_cell.value is None


def test_add_single_input():
    input_cell = basic.Variable(value=1)
    output_cell = basic.Variable()

    add = basic.Adder([input_cell], output_cell)
    add()

    assert output_cell.value == 1


def test_add_two_inputs():
    input_cell_1 = basic.Variable(value=1)
    input_cell_2 = basic.Variable(value=2)
    output_cell = basic.Variable()

    add = basic.Adder([input_cell_1, input_cell_2], output_cell)
    add()

    assert output_cell.value == 3


# =============================================================================
# Test is_value
def test_is_value():
    variable = basic.Variable(value=1)
    assert basic.is_value(variable)

# # =============================================================================
# # Test 'assign'
# def test_assignment():
#     input_1 = basic.Variable(value=1)
#     input_2 = basic.Variable(value=2)
#     output = basic.Variable()

#     assignment = basic.assign(output_cell, operator.add, input_1, input_2)
#     assignment()

#     assert output_cell.value == 3


# =============================================================================
# Test topological sorting


def is_before(node_1, node_2, ordering):
    return ordering.index(node_1) < ordering.index(node_2)


def test_topological_sort_empty():
    ordering = basic.topological_sort({})
    assert len(ordering) == 0


def test_topological_sort_circular_1():
    with pytest.raises(basic.GraphException) as e:
        ordering = basic.topological_sort({"A": ["A"]})
    assert str(e.value) == "Circular dependency detected in graph"


def test_topological_sort_one_dependency():
    ordering = basic.topological_sort({"B": ["A"]})
    assert ordering == ["A", "B"]


def test_topological_sort_circular_2():
    with pytest.raises(basic.GraphException) as e:
        ordering = basic.topological_sort({"A": ["B"], "B": ["A"]})
    assert str(e.value) == "Circular dependency detected in graph"


def test_topological_sort_diamond_1():
    ordering = basic.topological_sort({
        "D": ["C", "B"], "C": ["A"], "B": ["A"], "A": []
    })
    assert ordering[0] == "A"
    assert set(ordering[1:3]) == {"B", "C"}
    assert ordering[-1] == "D"


def test_topological_sort_circular_3():
    with pytest.raises(basic.GraphException) as e:
        ordering = basic.topological_sort({
            "D": ["C", "B"], "C": ["A"], "B": ["A"], "A": ["D"]
        })
    assert str(e.value) == "Circular dependency detected in graph"


def test_topological_sort_DAG():
    ordering = basic.topological_sort({
        "A": [], "B": [],
        "C": ["A", "B"], "D": ["A", "B"],
        "E": ["A", "C"], "F": ["B", "D"],
        "G": ["A", "E"],
        "H": ["B", "F"]
    })
    assert set(ordering[0:2]) == {"A", "B"}

    assert is_before("A", "C", ordering)
    assert is_before("B", "C", ordering)

    assert is_before("A", "D", ordering)
    assert is_before("B", "D", ordering)

    assert is_before("A", "E", ordering)
    assert is_before("C", "E", ordering)

    assert is_before("B", "F", ordering)
    assert is_before("D", "F", ordering)

    assert is_before("A", "G", ordering)
    assert is_before("E", "G", ordering)

    assert is_before("B", "H", ordering)
    assert is_before("F", "H", ordering)


# =============================================================================
# Test graph construction


def test_empty_graph():
    graph = basic.DependencyGraph({})
    assert graph.precedence_dict == {}
    assert graph.dependency_dict == {}


def test_singleton_graph():
    graph = basic.DependencyGraph({"A": set()})
    assert graph.precedence_dict == {"A": set()}
    assert graph.dependency_dict == {"A": set()}
    assert graph.input_nodes == {"A"}


def test_singleton_graph_2():
    graph = basic.DependencyGraph()
    assert graph.add_node("A") == "A"
    assert graph.precedence_dict == {"A": set()}
    assert graph.dependency_dict == {"A": set()}
    assert graph.input_nodes == {"A"}


def test_add_same_node_twice():
    graph = basic.DependencyGraph()
    assert graph.add_node("A") == "A"
    assert graph.add_node("A") == "A"
    assert graph.precedence_dict == {"A": set()}
    assert graph.dependency_dict == {"A": set()}
    assert graph.input_nodes == {"A"}


def test_one_edge_graph_1():
    graph = basic.DependencyGraph({"A": {"B"}, "B": set()})
    assert graph.precedence_dict == {"B": {"A"}, "A": set()}
    assert graph.dependency_dict == {"A": {"B"}, "B": set()}
    assert graph.input_nodes == {"B"}


def test_one_edge_graph_2():
    graph = basic.DependencyGraph()
    graph.add_dependency("B", "A")
    assert graph.precedence_dict == {"A": {"B"}, "B": set()}
    assert graph.dependency_dict == {"B": {"A"}, "A": set()}
    assert graph.input_nodes == {"A"}


def test_underspecified_graph():
    # DependencyGraph will add empty dependency set for "B"
    graph = basic.DependencyGraph({"A": {"B"}})
    assert graph.precedence_dict == {"B": {"A"}, "A": set()}
    assert graph.dependency_dict == {"A": {"B"}, "B": set()}
    assert graph.input_nodes == {"B"}


def test_precedence_dict_three_edges():
    # DependencyGraph will add empty dependency set for "A"
    graph = basic.DependencyGraph({"B": {"A"}, "C": {"A", "B"}})
    assert graph.precedence_dict == {"A": {"B", "C"}, "B": {"C"}, "C": set()}
    assert graph.dependency_dict == {"A": set(), "B": {"A"}, "C": {"A", "B"}}
    assert graph.input_nodes == {"A"}


def test_two_input_nodes():
    graph = basic.DependencyGraph({"C": {"A", "B"}})
    assert graph.input_nodes == {"A", "B"}


# =============================================================================
# Test graph decoration

# We use this IdNode class so that equality is done on object identity
# and not on the label value. We need to to make sure that the reference
# structure of the decorated graph is correct; in particular, that the
# same underlying node is not decorated twice if it appears in two different
# dependency sets


class IdNode:

    def __init__(self, label):
        self.label = label

    def __str__(self):
        return self.label


class Decorator:

    def __init__(self, node):
        self.node = node


def undecorate(decorator):
    return decorator.node


def test_decorate_empty():
    graph = basic.DependencyGraph({})
    decorated_graph = graph.decorate(lambda node: Decorator(node))
    assert len(graph) == 0


def test_decorate_singleton():
    node_a = IdNode("A")

    graph = basic.DependencyGraph({node_a: set()})
    decorated_graph = graph.decorate(lambda node: Decorator(node))
    assert len(decorated_graph) == 1
    assert len(decorated_graph.dependency_dict.keys()) == 1
    the_decorator = next(iter(decorated_graph.dependency_dict))
    assert the_decorator.node == node_a
    assert decorated_graph.dependency_dict[the_decorator] == set()


def test_decorated_two_node_graph():
    node_a = IdNode("A")
    node_b = IdNode("B")
    graph = basic.DependencyGraph({node_a: set(), node_b: {node_a}})
    decorated_graph = graph.decorate(lambda node: Decorator(node))
    undecorated_graph = decorated_graph.decorate(undecorate)
    assert undecorated_graph.dependency_dict == graph.dependency_dict


def test_decorated_three_node_graph():
    node_a = IdNode("A")
    node_b = IdNode("B")
    node_c = IdNode("C")
    graph = basic.DependencyGraph({node_a: set(), node_b: {node_a, node_c}})
    decorated_graph = graph.decorate(lambda node: Decorator(node))
    undecorated_graph = decorated_graph.decorate(undecorate)
    assert undecorated_graph.dependency_dict == graph.dependency_dict


def test_decorated_diamond():
    node_a = IdNode("A")
    node_b = IdNode("B")
    node_c = IdNode("C")
    node_d = IdNode("D")
    node_e = IdNode("E")
    graph = basic.DependencyGraph({
        node_b: {node_a},
        node_c: {node_a},
        node_d: {node_b, node_c, node_e}
    })
    decorated_graph = graph.decorate(lambda node: Decorator(node))
    undecorated_graph = decorated_graph.decorate(undecorate)
    assert undecorated_graph.dependency_dict == graph.dependency_dict


# =============================================================================
# Test topological queue


def test_topological_queue_empty():
    queue = basic.TopologicalQueue(basic.DependencyGraph({}))
    assert queue.empty()


def test_topological_queue_singleton():
    queue = basic.TopologicalQueue(basic.DependencyGraph({"A": {}}))
    assert not queue.empty()
    assert queue.ready_set() == {"A"}


def test_topological_queue_cycle():
    with pytest.raises(basic.CircularDependency) as e:
        queue = basic.TopologicalQueue(basic.DependencyGraph({"A": {"A"}}))
    assert str(e.value) == "Circular dependency detected in graph"


def test_topological_queue_two_independent_nodes():
    graph = basic.DependencyGraph({"A": {}, "B": {}})
    queue = basic.TopologicalQueue(graph)
    assert not queue.empty()
    assert queue.ready_set() == {"A", "B"}
    now_ready = queue.completed("B")
    assert queue.ready_set() == {"A"}
    # Nothing depends on "A" so its completion does not activate any
    # nodes
    assert now_ready == set()


def test_topological_queue_bug():
    graph = basic.DependencyGraph()
    graph.add_node("A")
    graph.add_node("B")
    queue = basic.TopologicalQueue(graph)
    assert queue.ready_set() == {"A", "B"}


def test_topological_queue_two_dependent_nodes():
    graph = basic.DependencyGraph({"A": set(), "B": {"A"}})
    queue = basic.TopologicalQueue(graph)
    assert not queue.empty()
    assert len(queue) == 2
    assert queue.ready_set() == {"A"}
    now_ready = queue.completed("A")

    # There was a bug that resulted in the LHS of the following actually
    # being equal to an empty set
    assert graph.dependency_dict["B"] == {"A"}

    assert len(queue) == 1
    assert queue.ready_set() == {"B"}
    assert now_ready == {"B"}
    now_ready = queue.completed("B")
    assert len(queue) == 0
    assert queue.ready_set() == set()
    assert queue.empty()
    assert now_ready == set()

    assert graph.dependency_dict["A"] == set()
    # There was a bug that resulted in the LHS of the following actually
    # being equal to an empty set
    assert graph.dependency_dict["B"] == {"A"}


def test_topological_queue_diamond():
    queue = basic.TopologicalQueue(basic.DependencyGraph({
        "A": {},
        "B": {"A"},
        "C": {"A"},
        "D": {"B", "C"}
    }))

    assert not queue.empty()
    assert len(queue) == 4
    ready_set_a = queue.ready_set()
    assert ready_set_a == {"A"}

    now_ready_a = queue.completed("A")
    assert ready_set_a == {"A"}
    ready_set_bc = queue.ready_set()
    assert ready_set_bc == {"B", "C"}
    assert now_ready_a == {"B", "C"}
    assert len(queue) == 3
    assert not queue.empty()

    now_ready_b = queue.completed("B")
    assert queue.ready_set() == {"C"}
    assert now_ready_b == set()
    assert len(queue) == 2
    assert not queue.empty()

    # Make sure this didn't change under our feet
    assert now_ready_a == {"B", "C"}

    now_ready = queue.completed("C")
    assert queue.ready_set() == {"D"}
    assert now_ready == {"D"}
    assert len(queue) == 1
    assert not queue.empty()

    with pytest.raises(KeyError):
        queue.completed("C")

    now_ready = queue.completed("D")
    assert queue.ready_set() == set()
    assert now_ready == set()
    assert len(queue) == 0
    assert queue.empty()


# ===========================================================================
# Test TopologicalComputer


def test_null_execution():
    graph = basic.DependencyGraph()
    basic.compute_sequential(graph)


def test_single_dependency():

    input_cell = basic.Variable(name="input_cell", value=99)
    output_cell = basic.Variable(name="output_cell")
    add = basic.Adder([input_cell], output_cell)

    graph = basic.DependencyGraph()
    basic.compute_sequential(graph)

    assert output_cell.value is None

    graph.add_dependency(add, input_cell)
    graph.add_dependency(output_cell, add)
    basic.compute_sequential(graph)

    assert output_cell.value == 99

    input_cell.value = 87
    basic.compute_sequential(graph)
    assert output_cell.value == 87


def test_add_precedence():

    # add_precedence(A, B) is a synonym for add_dependency(B, A)

    input_cell = basic.Variable(name="input_cell", value=99)
    output_cell = basic.Variable(name="output_cell")
    add = basic.Adder([input_cell], output_cell)

    graph = basic.DependencyGraph()
    basic.compute_sequential(graph)

    assert output_cell.value is None

    graph.add_precedence(input_cell, add)
    graph.add_precedence(add, output_cell)
    basic.compute_sequential(graph)

    assert output_cell.value == 99

    input_cell.value = 87
    basic.compute_sequential(graph)
    assert output_cell.value == 87


# CellWrapper is for instrumenting cells so that the computation order
# can be recorded. This is used to ensure that the evaluation order is
# correct.


class CellWrapper:

    def __init__(self, real_cell, compute_list):
        self.real_cell = real_cell
        self.compute_list = compute_list

    def __call__(self):
        self.compute_list.append(self.real_cell)
        self.real_cell()


def test_two_dependencies():

    input_cell_1 = basic.Variable(name="input_cell_1", value=1)
    input_cell_2 = basic.Variable(name="input_cell_2", value=2)
    child_cell_1 = basic.Variable(name="child_cell_1")
    child_cell_2 = basic.Variable(name="child_cell_2")
    output_cell = basic.Variable(name="output_cell")

    add_1 = basic.Adder([input_cell_1, input_cell_2], child_cell_1)
    add_2 = basic.Adder([input_cell_1, input_cell_2], child_cell_2)

    add_3 = basic.Adder([child_cell_1, child_cell_2], output_cell)

    graph = basic.DependencyGraph()

    # No dependencies declared yet
    basic.compute_sequential(graph)

    assert output_cell.value is None

    wrappers = {}
    computed_order = []

    def wrapper(cell):
        result = wrappers.get(cell, None)
        if not result:
            result = CellWrapper(cell, computed_order)
            wrappers[cell] = result
        return result

    # ======================================================================
    # Add a dependency and make sure that the computation order is correct.
    graph.add_dependency(wrapper(add_1), wrapper(input_cell_1))
    basic.compute_sequential(graph)

    assert len(computed_order) == 2
    assert is_before(input_cell_1, add_1, computed_order)

    # ======================================================================
    # Add a dependency and make sure that the computation order is correct.
    graph.add_dependency(wrapper(add_1), wrapper(input_cell_2))

    computed_order.clear()
    assert len(computed_order) == 0
    basic.compute_sequential(graph)

    assert len(computed_order) == 3
    assert is_before(input_cell_1, add_1, computed_order)
    assert is_before(input_cell_2, add_1, computed_order)

    # ======================================================================
    # Add more dependencies and make sure that the computation order is
    # correct.
    graph.add_dependency(wrapper(child_cell_1), wrapper(add_1))
    graph.add_dependency(wrapper(add_2), wrapper(input_cell_1))
    graph.add_dependency(wrapper(add_2), wrapper(input_cell_2))
    graph.add_dependency(wrapper(child_cell_2), wrapper(add_2))
    graph.add_dependency(wrapper(add_3), wrapper(child_cell_1))
    graph.add_dependency(wrapper(add_3), wrapper(child_cell_2))
    graph.add_dependency(wrapper(output_cell), wrapper(add_3))

    computed_order.clear()
    assert len(computed_order) == 0
    basic.compute_sequential(graph)
    assert len(computed_order) == 8

    assert is_before(input_cell_1, add_1, computed_order)
    assert is_before(input_cell_2, add_1, computed_order)
    assert is_before(input_cell_1, add_2, computed_order)
    assert is_before(input_cell_2, add_2, computed_order)
    assert is_before(add_1, child_cell_1, computed_order)
    assert is_before(add_2, child_cell_2, computed_order)
    assert is_before(child_cell_1, add_3, computed_order)
    assert is_before(child_cell_2, add_3, computed_order)
    assert is_before(add_3, output_cell, computed_order)

    assert output_cell.value == 6

    input_cell_2.value = 3
    basic.compute_sequential(graph)
    assert output_cell.value == 8


def test_singleton_cell():
    graph = basic.DependencyGraph()

    singleton = basic.Variable(name="singleton", value=1)

    computed_cells = []
    singleton_wrapper = CellWrapper(singleton, computed_cells)
    assert graph.add_node(singleton_wrapper) is singleton_wrapper

    assert computed_cells == []
    basic.compute_sequential(graph)
    assert computed_cells == [singleton]


def test_null_parameters():
    graph = basic.DependencyGraph()

    with pytest.raises(ValueError) as e:
        graph.add_node(None)
    assert str(e.value) == "Invalid argument: node=None"

    with pytest.raises(ValueError) as e:
        graph.add_dependency(None, "A")
    assert str(e.value) == "Invalid argument: from_cell=None"

    with pytest.raises(ValueError) as e:
        graph.add_dependency("A", None)
    assert str(e.value) == "Invalid argument: to_cell=None"

    with pytest.raises(ValueError) as e:
        graph.add_dependency(None, None)
    assert str(e.value) == "Invalid argument: from_cell=None"
