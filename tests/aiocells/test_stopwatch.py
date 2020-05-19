
from datetime import datetime, timedelta

import aiocells.stopwatch


def seconds(i):
    return timedelta(seconds=i)


def test_stopwatch_elapsed_time():

    current_time = datetime(2016, 1, 1)

    def now_function():
        return current_time

    stopwatch = aiocells.stopwatch.Stopwatch(now_function=now_function)

    assert stopwatch.elapsed_time() is None

    stopwatch.start()

    current_time += seconds(60)

    assert stopwatch.elapsed_time() == seconds(60)

    current_time += seconds(120)

    assert stopwatch.elapsed_time() == seconds(180)

    current_time += seconds(30)

    stopwatch.stop()
    assert stopwatch.elapsed_time() == seconds(210)

    current_time += seconds(30)
    stopwatch.start()
    current_time += seconds(10)
    assert stopwatch.elapsed_time() == seconds(10)


def test_lap_time():

    current_time = datetime(2016, 1, 1)

    def now_function():
        return current_time

    stopwatch = aiocells.stopwatch.Stopwatch(now_function=now_function)

    assert stopwatch.elapsed_time() is None

    stopwatch.start()

    current_time += timedelta(minutes=1)

    assert stopwatch.elapsed_time(return_lap_time=True) \
        == (seconds(60), seconds(60))

    current_time += timedelta(minutes=2)

    assert stopwatch.elapsed_time(return_lap_time=True) \
        == (seconds(180), seconds(120))

    current_time += timedelta(seconds=30)

    stopwatch.stop()
    stopwatch.elapsed_time(return_lap_time=True) == (seconds(210), seconds(30))

    current_time += timedelta(seconds=30)
    stopwatch.start()
    current_time += timedelta(seconds=10)
    stopwatch.elapsed_time(return_lap_time=True) == (seconds(10), seconds(10))
