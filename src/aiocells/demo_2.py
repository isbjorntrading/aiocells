#!/usr/bin/env python3

import aiocells


class HelloWorld:

    def __call__(self):
        print("Hello, world!")


def main():
    graph = aiocells.DependencyGraph()

    # In this example, we add a instance of a callable object rather than
    # a function
    node = graph.add_node(HelloWorld())

    aiocells.compute_sequential(graph)
