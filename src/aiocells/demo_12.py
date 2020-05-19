#!/usr/bin/env python3

import aiocells

# Demonstrates modification tracking nodes. Nodes only compute if one or
# more of their dependencies have actually changed as signalled by the
# 'mod_time' attribute. To record 'mod_time' when a node changes, a mod.Clock
# is used, which always returns a new, higher value when the method 'now' is
# called.


def main():
    graph = aiocells.DependencyGraph()

    clock = aiocells.ModClock()

    variable_1 = aiocells.ModVariable(clock)
    variable_2 = aiocells.ModVariable(clock)

    printer_1 = aiocells.ModPrinter(clock, variable_1,
                                    "variable_1 changed to {value}")
    printer_2 = aiocells.ModPrinter(clock, variable_2,
                                    "variable_2 changed to {value}")

    graph.add_precedence(variable_1, printer_1)
    graph.add_precedence(variable_2, printer_2)

    print("Nothing has changed:")
    aiocells.compute_sequential(graph)

    variable_1.value = 1
    variable_2.value = 2
    print("Both variables:")
    aiocells.compute_sequential(graph)

    variable_1.value = 3
    print("variable_1 only:")
    aiocells.compute_sequential(graph)
