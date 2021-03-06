import aiocells
import aiocells.basic as basic
import aiocells.aio as aio
import aiocells.mod as mod
import aiocells.flow as flow


def test_basic():
    assert aiocells.DependencyGraph is basic.DependencyGraph
    assert aiocells.Place is basic.Place
    assert aiocells.compute_sequential is basic.compute_sequential
    assert aiocells.Stopwatch is basic.Stopwatch
    assert aiocells.print_value is basic.print_value
    assert aiocells.assign is basic.assign


def test_aio():
    assert aiocells.async_compute_sequential is aio.async_compute_sequential
    assert aiocells.async_compute_concurrent is aio.async_compute_concurrent
    assert aiocells.async_compute_concurrent_simple is \
        aio.async_compute_concurrent_simple
    assert aiocells.timer is aio.timer


def test_mod():
    assert aiocells.ModClock is mod.ModClock
    assert aiocells.ModPlace is mod.ModPlace
    assert aiocells.ModPrinter is mod.ModPrinter


def test_flow():
    assert aiocells.compute_flow is flow.compute_flow
