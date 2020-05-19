#!/usr/bin/env python3

import time

import isbjorn.incubator.cells.basic as basic


def main():
    graph = basic.DependencyGraph()
    graph.add_node(lambda: time.sleep(2))
    print("This computation will take about 2 seconds because of the sleep")
    basic.compute_sequential(graph)
