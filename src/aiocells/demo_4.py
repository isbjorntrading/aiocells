#!/usr/bin/env python3

import time

import aiocells


def main():
    graph = aiocells.DependencyGraph()

    # 'add_node' always returns the node that has just been added, in this
    # case the lambda functions. We will use this below to define precedence
    # relationships
    print_sleeping = graph.add_node(lambda: print("Sleeping..."))
    sleep = graph.add_node(lambda: time.sleep(2))
    print_woke_up = graph.add_node(lambda: print("Woke up!"))

    print("Define the precedence relationships...")
    graph.add_precedence(print_sleeping, sleep)
    graph.add_precedence(sleep, print_woke_up)

    # Now, after we've defined the precedence relationships, we use the
    # simplest computer to compute the graph. The nodes will be called in
    # an order that is consistent with the precedence relationships.
    # Specifically, the nodes are executed in topological order.
    aiocells.compute_sequential(graph)
