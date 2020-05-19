import asyncio
import inspect
import logging

import aiocells.basic as basic
import aiocells.aio as aio


class ModClock:

    def __init__(self):
        self._now = 0

    def now(self):
        self._now += 1
        return self._now

    @property
    def current_value(self):
        return self._now


class ModVariable:

    def __init__(self, clock):
        self._clock = clock
        self._value = None
        self._new_value = None
        self.mod_time = None

    @property
    def value(self):
        return self._value

    @property
    def new_value(self):
        return self._new_value

    @value.setter
    def value(self, value):
        self._new_value = value

    @property
    def is_dirty(self):
        return self._value != self._new_value

    def __call__(self):
        if not self.is_dirty:
            return
        self.mod_time = self._clock.now()
        self._value = self._new_value


class ModAdder:

    def __init__(self, clock, input_cells, output_cell):
        self.clock = clock
        self.input_cells = input_cells
        self.output_cell = output_cell
        self.mod_time = None

    def __call__(self):
        requires_recalc = self.mod_time is None or any(
            input_cell.mod_time > self.mod_time
            for input_cell in self.input_cells
        )
        if not requires_recalc:
            return
        self.output_cell.value = sum(v.value for v in self.input_cells)
        self.mod_time = self.clock.now()


class ModPrinter:

    def __init__(self, clock, input_cell, message):
        self.clock = clock
        self.input_cell = input_cell
        self.message = message
        self.mod_time = None

    def __call__(self):
        if self.input_cell.mod_time is None:
            return
        assert self.input_cell.mod_time is not None
        if self.mod_time is not None \
           and self.mod_time >= self.input_cell.mod_time:
            return
        print(self.message.format(value=self.input_cell.value))
        self.mod_time = self.clock.now()
