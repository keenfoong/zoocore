import threading


class Threaded(object):
    """Threaded base class that contains a threading.Lock member and an
    'exclusive' function decorator that implements exclusive access
    to the contained code using a thread lock.
    """

    def __init__(self):
        self._lock = threading.Lock()

    @staticmethod
    def exclusive(func):
        """
        Static method intended to be used as a function decorator in derived
        classes.
        :param func: Function to decorate/wrap
        :returns: Wrapper function that executes the function inside the acquired lock
        ::example:
                @Threaded.exclusive
                def my_method(self, ...):
                    ...
        """

        def wrapper(self, *args, **kwargs):
            """
            Internal wrapper method that executes the function with the specified arguments
            inside the acquired lock

            :param *args: The function parameters
            :param **kwargs: The function named parameters
            :returns: The result of the function call
            """
            with self._lock:
                return func(self, *args, **kwargs)

        return wrapper