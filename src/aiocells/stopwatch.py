import datetime


class Stopwatch:

    def __init__(
        self,
        stop_message=None,
        writer=print,
        now_function=datetime.datetime.utcnow
    ):
        self.__now = now_function
        self.__is_running = False
        self.__start_time = None
        self.__lap_start_time = None
        self.__stop_message = stop_message
        self.__writer = writer

    @property
    def is_running(self):
        return self.__is_running

    def start(self):
        assert not self.__is_running
        self.__start_time = self.now()
        self.__lap_start_time = self.__start_time
        self.__is_running = True

    def stop(self):
        assert self.__is_running
        self.__stop_time = self.now()
        self.__is_running = False

    def restart(self):
        self.stop()
        self.start()

    def elapsed_time(self, return_lap_time=False):
        elapsed_time_result = None
        lap_time_result = None
        if self.__start_time is None:
            elapsed_time_result = None
            lap_time_result = None
        elif self.__is_running:
            now = self.now()
            elapsed_time_result = now - self.__start_time
            lap_time_result = now - self.__lap_start_time
            if return_lap_time:
                self.__lap_start_time = now
        else:
            elapsed_time_result = self.__stop_time - self.__start_time
            lap_time_result = self.__stop_time - self.__lap_start_time

        if return_lap_time:
            return (elapsed_time_result, lap_time_result)
        else:
            return elapsed_time_result

    def now(self):
        return self.__now()

    # Context manager methods

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.stop()
        if self.__stop_message and not traceback:
            self.__writer(self.__stop_message.format(
                elapsed_time=self.elapsed_time()
            ))
        if traceback:
            return False
        return True
