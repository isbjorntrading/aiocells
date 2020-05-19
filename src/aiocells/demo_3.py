#!/usr/bin/env python3

import time

import aiocells


def main():
    graph = aiocells.DependencyGraph()
    graph.add_node(lambda: time.sleep(2))
    print("This computation will take about 2 seconds because of the sleep")
    aiocells.compute_sequential(graph)
