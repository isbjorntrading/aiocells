#!/usr/bin/env python3

import isbjorn.incubator.cells.basic as basic
import isbjorn.incubator.cells.mod as mod

# Demonstrates modification tracking nodes. Nodes only compute if one or
# more of their dependencies have actually changed as signalled by the
# 'mod_time' attribute. To record 'mod_time' when a node changes, a mod.Clock
# is used, which always returns a new, higher value when the method 'now' is
# called.


def main():
    graph = basic.DependencyGraph()

    clock = mod.Clock()

    variable_1 = mod.ModVariable(clock)
    variable_2 = mod.ModVariable(clock)

    printer_1 = mod.ModPrinter(clock, variable_1,
                               "  variable_1 changed to {value}")
    printer_2 = mod.ModPrinter(clock, variable_2,
                               "  variable_2 changed to {value}")

    graph.add_precedence(variable_1, printer_1)
    graph.add_precedence(variable_2, printer_2)

    print("Nothing has changed:")
    basic.compute_sequential(graph)

    variable_1.value = 1
    variable_2.value = 2
    print("Both variables:")
    basic.compute_sequential(graph)

    variable_1.value = 3
    print("variable_1 only:")
    basic.compute_sequential(graph)
