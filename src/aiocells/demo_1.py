#!/usr/bin/env python3

import aiocells


def hello_world():
    print("Hello, world!")


def main():
    graph = aiocells.DependencyGraph()

    # The node can be any callable, in this case a function.
    graph.add_node(hello_world)
    aiocells.compute_sequential(graph)
