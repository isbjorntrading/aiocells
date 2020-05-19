#!/usr/bin/env python3

import aiocells.basic as basic


def hello_world():
    print("Hello, world!")


def main():
    graph = basic.DependencyGraph()

    # The node can be any callable, in this case a function.
    graph.add_node(hello_world)
    basic.compute_sequential(graph)
