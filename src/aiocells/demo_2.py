#!/usr/bin/env python3

import aiocells.basic as basic


class HelloWorld:

    def __call__(self):
        print("Hello, world!")


def main():
    graph = basic.DependencyGraph()

    # In this example, we add a instance of a callable object rather than
    # a function
    node = graph.add_node(HelloWorld())

    basic.compute_sequential(graph)
