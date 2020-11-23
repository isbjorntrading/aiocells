import aiocells.basic as basic
import aiocells.mod as mod


def test_virtual_clock():
    clock = mod.ModClock()
    assert clock.now() == 1
    assert clock.current_value == 1
    assert clock.current_value == 1

    assert clock.now() == 2
    assert clock.current_value == 2
    assert clock.current_value == 2

    assert clock.now() == 3


def test_mod_variable():
    clock = mod.ModClock()
    variable = mod.ModPlace(clock)

    assert clock.current_value == 0

    assert variable.value is None
    assert not variable.is_dirty
    variable.value = 42
    assert variable.is_dirty
    assert variable.value is None
    assert variable.new_value == 42

    assert clock.current_value == 0
    variable()
    assert clock.current_value == 1
    assert variable.mod_time == 1
    assert variable.value == 42
    assert not variable.is_dirty

    # Place hasn't changed
    assert clock.current_value == 1
    variable()
    assert clock.current_value == 1
    assert variable.mod_time == 1
    assert variable.value == 42
    assert not variable.is_dirty

    assert clock.current_value == 1
    variable.value = 888
    assert variable.value == 42
    assert variable.new_value == 888
    assert variable.is_dirty
    assert variable.mod_time == 1

    assert clock.current_value == 1
    variable()
    assert clock.current_value == 2
    assert variable.mod_time == 2
    assert not variable.is_dirty
    assert variable.value == 888


def test_mod_adder_no_inputs():
    clock = mod.ModClock()

    output_cell = mod.ModPlace(clock)

    adder = mod.ModAdder(clock, [], output_cell)
    adder()
    assert adder.mod_time == 1
    assert output_cell.value is None

    adder()
    assert adder.mod_time == 1
    assert output_cell.value is None


def test_mod_adder_one_input():
    clock = mod.ModClock()

    input_cell = mod.ModPlace(clock)
    output_cell = mod.ModPlace(clock)
    adder = mod.ModAdder(clock, [input_cell], output_cell)

    assert not input_cell.is_dirty
    input_cell.value = 79
    assert input_cell.is_dirty
    input_cell()
    assert clock.current_value == 1
    assert input_cell.mod_time == 1
    assert not input_cell.is_dirty

    assert adder.mod_time is None
    adder()
    assert clock.current_value == 2
    assert input_cell.mod_time == 1
    assert adder.mod_time == 2
    assert output_cell.is_dirty
    assert output_cell.value is None

    assert output_cell.mod_time is None
    output_cell()
    assert clock.current_value == 3
    assert input_cell.mod_time == 1
    assert adder.mod_time == 2
    assert output_cell.mod_time == 3
    assert not output_cell.is_dirty
    assert output_cell.value == 79

    assert clock.current_value == 3
    assert not input_cell.is_dirty
    input_cell.value = 88
    assert input_cell.is_dirty
    input_cell()
    assert clock.current_value == 4
    assert input_cell.mod_time == 4
    assert not input_cell.is_dirty

    assert clock.current_value == 4
    assert adder.mod_time == 2
    adder()
    assert clock.current_value == 5
    assert adder.mod_time == 5
    assert output_cell.is_dirty

    assert clock.current_value == 5
    assert output_cell.is_dirty
    output_cell()
    assert clock.current_value == 6
    assert adder.mod_time == 5
    assert output_cell.mod_time == 6
    assert not output_cell.is_dirty
    assert output_cell.value == 88


def test_mod_adder_two_inputs():
    clock = mod.ModClock()

    input_cell_1 = mod.ModPlace(clock)
    input_cell_2 = mod.ModPlace(clock)
    output_cell = mod.ModPlace(clock)

    input_cell_1.value = 1
    input_cell_2.value = 2
    adder = mod.ModAdder(clock, [input_cell_1, input_cell_2], output_cell)

    assert input_cell_1.is_dirty
    input_cell_1()
    assert not input_cell_1.is_dirty

    assert input_cell_2.is_dirty
    input_cell_2()
    assert not input_cell_2.is_dirty

    adder()

    assert output_cell.is_dirty
    output_cell()
    assert not output_cell.is_dirty
    assert output_cell.value == 3

    input_cell_1.value = 11
    input_cell_1()
    input_cell_2()
    adder()
    output_cell()

    assert not output_cell.is_dirty
    assert output_cell.value == 13


def test_mod_adder_two_inputs_with_graph():

    clock = mod.ModClock()
    graph = basic.DependencyGraph()

    input_cell_1 = mod.ModPlace(clock)
    input_cell_2 = mod.ModPlace(clock)
    irrelevant_input = mod.ModPlace(clock)
    output_cell = mod.ModPlace(clock)

    adder = mod.ModAdder(clock, [input_cell_1, input_cell_2], output_cell)

    graph.add_node(irrelevant_input)
    graph.add_precedence(input_cell_1, adder)
    graph.add_precedence(input_cell_2, adder)
    graph.add_precedence(adder, output_cell)

    input_cell_1.value = 1
    input_cell_2.value = 2
    basic.compute_sequential(graph)
    assert not output_cell.is_dirty
    assert output_cell.value == 3
    assert clock.current_value == 4
    assert output_cell.mod_time == 4

    input_cell_1.value = 11
    basic.compute_sequential(graph)
    assert not output_cell.is_dirty
    assert output_cell.value == 13
    assert clock.current_value == 7
    assert output_cell.mod_time == 7

    # A cell that does not affect anything else is modified.
    # The output_cell mod_time is unaffected.
    irrelevant_input.value = 77
    basic.compute_sequential(graph)
    assert irrelevant_input.value == 77
    assert clock.current_value == 8
    assert irrelevant_input.mod_time == 8
    assert output_cell.mod_time == 7
