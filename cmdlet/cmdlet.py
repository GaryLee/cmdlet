#!python
# codatag: utf-8

"""This module provides a pipe-like mechanism to cascade commands."""

import copy

class UnregisteredPipeType(Exception):
    """Exception for unknown data type when cascading pipes.

    If the type of pipe item is not registered in Pipe class, this exception
    will be raised.
    """
    def __init__(self, item_type):
        super(UnregisteredPipeType, self).__init__('Unregistered type: %s' % repr(item_type))

class Pipe(object):
    """Pipe is a wrapper for generator function. Pipe object support "|"
    operator and uses it to cascade generator functions. A set of cascading pipe
    objects can then be invoked by Pipe.iter(), Pipe.run() and Pipe.result()
    method.
    """

    #: A dictionary to map data type and pipe creator.
    pipe_item_types = {}

    def __init__(self, func, *args, **kw):
        """Constructor of Pipe. It takes first argument as a generator function.
        args and kw are default arguments to be used if the Pipe object is
        cascaded directly. The default arguments are replaced by the arguments of
        __call__ operator.

        :param self: self reference.
        :param func: The generator function to be be wrapped.
        :param args: The default arguments to be used for generator function.
        :param kw:  The default keyword arguments to be used for generator function.
        """
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.func = func
        self.next = None
        self.chained = False
        self.args = args
        self.kw = kw

    def __or__(self, next):
        """Set operand of right-hand side to be next Pipe object. Type convertion
        will be applied automatically if next is not a Pipe object and its type
        is registered in Pipe.pipe_item_types. Otherwise, UnregisteredPipeType
        will be raised.

        :param next: The next Pipe object to be cascaded.
        :type next: Pipe object or any object whose type is registered.

        :returns: The clone of self.
        """
        if not isinstance(next, Pipe):
            item_creator = get_item_creator(type(next))
            if item_creator is None:
                raise UnregisteredPipeType(type(next))
            next = item_creator(next)

        # Self-cloning here is used to avoid conflict when Pipe object
        # is refered more than once.
        clone = self.clone()
        if not next.chained:
            clone.append(next)
        else:
            clone.append(next(*next.args, **next.kw))
        return clone

    def __ror__(self, prev):
        """Set operand of left-hand side to be previous Pipe object. Type
        convertion will be applied automatically if prev is not a Pipe object
        and its type is registered in Pipe.pipe_item_types. Otherwise,
        UnregisteredPipeType will be raised.

        :param prev: The previous Pipe object which used to cascade this object.
        :type prev: Pipe object or any object whose type is registered.

        :returns: previous Pipe object.
        """
        if not isinstance(prev, Pipe):
            item_creator = get_item_creator(type(prev))
            if item_creator is None:
                raise UnregisteredPipeType(type(prev))
            prev = item_creator(prev)
        return prev.__or__(self)

    def __call__(self, *args,**kw):
        """A Pipe object to be called means self-cloning with new default
        arguments.

        :param args: The default arguments to be used for generator function.
        :param kw:  The default keyword arguments to be used for generator function.

        :returns: The clone of self.
        """
        clone = self.clone()
        clone.chained = False
        clone.args = args;
        clone.kw = kw
        return clone

    def clone(self):
        """Self-cloning. All its next Pipe objects are cloned too.

        :returns: cloned object
        """
        new_object = copy.copy(self)
        if new_object.next:
            new_object.next = new_object.next.clone()
        return new_object

    def append(self, next):
        """Append next object to pipe tail.

        :param next: The Pipe object to be appended to tail.
        :type next: Pipe object.
        """
        next.chained = True
        if self.next:
            self.next.append(next)
        else:
            self.next = next

    def __iter__(self):
        """Make iterator.

        :returns: iterator object.
        """
        return self.iter()

    def iter(self, prev=None):
        """Return an generator as iterator object.

        :param prev: Previous Pipe object which used for data input.
        :returns: A generator for iteration.
        """

        if self.next:
            generator = self.next.iter(self.func(prev, *self.args, **self.kw))
        else:
            generator = self.func(prev, *self.args, **self.kw)
        return generator

    def run(self):
        """Execute the cascading pipe and return the last data processed by
        pipes.

        :returns: The last processed data.
        """
        last_data = None
        for last_data in self.iter():
            pass
        return last_data

    def result(self):
        """Execute the cascading pipe and return a list which contains all
        processed data.

        :returns: The list of processed data.
        :rtype: list
        """
        return list(self.iter())

def register_type(item_type, item_creator):
    """Register data type to Pipe class. Check :py:meth:`Pipe.__or__` and
    :py:meth:`Pipe.__ror__` for detail.

    :param item_type: The type of data object which used in pipe cascading.
    :param item_creator: A function to convert data to Pipe object.
    """
    Pipe.pipe_item_types[item_type] = item_creator

def unregister_type(item_type):
    """Unregister data type from Pipe class. Check Pipe.__or__ and Pipe.__ror__ for
    detail.

    :param item_type: The type of data object which used in pipe cascading.
    """
    if item_type not in Pipe.pipe_item_types:
        return
    del Pipe.pipe_item_types[item_type]

def unregister_all_types():
    """Unregister all data types from Pipe class."""
    Pipe.pipe_item_types.clear()

def has_registered_type(item_type):
    """Check if item_type is registered or not.

    :param item_type: The type to be checked.
    :returns: True: The item_type is registered. False: The item_type is not registered.
    :rtype: bool
    """
    return item_type in Pipe.pipe_item_types

def get_item_creator(item_type):
    """Get item creator according registered item type.

    :param item_type: The type of item to be checed.
    :type item_type: types.TypeType.
    :returns: Creator function. None if type not found.
    """
    if item_type not in Pipe.pipe_item_types:
        for registered_type in Pipe.pipe_item_types:
            if issubclass(item_type, registered_type):
                return Pipe.pipe_item_types[registered_type]
        return None
    else:
        return Pipe.pipe_item_types[item_type]


class PipeFunction:
    """Collection of basic Pipe wrappers."""
    @staticmethod
    def func(generator):
        """Wrap a generator function to Pipe object.

        :param generator: The generator function to be wrapped.
        :type generator: generator
        :returns: Pipe object
        """
        return Pipe(generator)

    @staticmethod
    def map(func):
        """Wrap a map function to Pipe object. Map function is a function with
        at least one argument. It is used to convert data. The first argument
        is the data to be converted. The return data from map function will
        be sent to next generator.

        :param func: The map function to be wrapped.
        :type func: function object
        :param args: The default arguments to be used for map function.
        :param kw:  The default keyword arguments to be used for map function.
        :returns: Pipe object
        """
        def wrapper(prev, *argv, **kw):
            if prev is None:
                raise TypeError('A mapper must have input.')
            for i in prev:
                yield func(i, *argv, **kw)
        return Pipe(wrapper)

    @staticmethod
    def filter(func):
        """Wrap a filter function to Pipe object. Filter function is a function
        with at least one argument. It is used to determine if the data can pass.
        The first argument is the data to be converted. The return data from
        filter function should be a boolean value. If true, data can pass.
        Otherwise, data is omitted.

        :param func: The filter function to be wrapped.
        :type func: function object
        :param args: The default arguments to be used for filter function.
        :param kw:  The default keyword arguments to be used for filter function.
        :returns: Pipe object
        """
        def wrapper(prev, *argv, **kw):
            if prev is None:
                raise TypeError('A filter must have input.')
            for i in prev:
                if func(i, *argv, **kw):
                    yield i
        return Pipe(wrapper)

    @staticmethod
    def reduce(func):
        """Wrap a reduce function to Pipe object. Reduce function is a function
        with at least two arguments. It works like built-in reduce function.
        It takes first argument for accumulated result, second argument for
        the new data to process. A keyword-based argument named 'init' is
        optional. If init is provided, it is used for the initial value of
        accumulated result. Or, the initial value is None.

        The first argument is the data to be converted. The return data from
        filter function should be a boolean value. If true, data can pass.
        Otherwise, data is omitted.

        :param func: The filter function to be wrapped.
        :type func: function object
        :param args: The default arguments to be used for filter function.
        :param kw: The default keyword arguments to be used for filter function.
        :returns: Pipe object
        """
        def wrapper(prev, *argv, **kw):
            accum_value = None if 'init' not in kw else kw.pop('init')
            if prev is None:
                raise TypeError('A reducer must have input.')
            for i in prev:
                accum_value = func(accum_value, i, *argv, **kw)
            yield accum_value
        return Pipe(wrapper)


    @staticmethod
    def stopper(func):
        """Wrap a conditoinal function(stopper function) to Pipe object.

        wrapped function should return boolean value. The cascading pipe will
        stop the execution if wrapped function return True.

        Stopper is useful if you have unlimited number of input data.

        :param func: The conditoinal function to be wrapped.
        :type func: function object
        :param args: The default arguments to be used for wrapped function.
        :param kw:  The default keyword arguments to be used for wrapped function.
        :returns: Pipe object
        """
        def wrapper(prev, *argv, **kw):
            if prev is None:
                raise TypeError('A stopper must have input.')
            for i in prev:
                if func(i, *argv, **kw):
                    break
                yield i
        return Pipe(wrapper)
