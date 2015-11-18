# What is cmdlet?

Cmdlet provides pipe-like mechanism to cascade functions and generators. It
uses symbol(**|**) to convert function to Pipe object and cascade them. This
sequence of commands can be executed and evaluated later. Just like the pipe
mechanism in Unix shell. For example:

```python
    from cmdlet.cmds import *

    # Create piped commands.
    cmds = range(10) | pipe.filter(lambda x: x > 5) | format('item#%d')

    # Execute commands and return the last processed data.
    run(cmds)
    # >>> 'item#9'

    # Execute commands and return processed data in a list.
    result(cmds)
    # >>> ['item#6', 'item#7', 'item#8', 'item#9']

    # Execute commands and return iterator for processed data.
    for data in cmds:
        print data
    # >>> item#6
    # >>> item#7
    # >>> item#8
    # >>> item#9

```

First, we created commands and use **|** to cascade them. Then, we execute
commands by run(), result() or iterator.

cmdlet can convert corresponding types to Pipe object automatically. In above
example, range(10) is a iterator not a Pipe object. Because second item is
a Pipe object(made by pipe.filter), it turns out first item to be converted
to a Pipe object automatically.

> NOTE:
> When using cmdlet's pipe mechanism, make sure one of your
> **first two pipe items** is a valid Pipe object.


# Run piped commands and get result

There are 3 ways to execute piped commands and get the result.

1. Use **run(cmds)** or **cmds.run()** to execute cmds and get the last
   processed data. Use this if you don't need all processed data. Or, the tasks
   you need to do have been done by cascaded Pipe objects.

2. Use **result(cmds)** or **cmds.result()** to get the processed data in a list.
   Use this method when you need to take all processed data to other mechanisms.

3. Use cmds as a **iterator** to handle the processed data one by one. It treats
   cascaded Pipe objects as a pre-processing function. Use it to process data and
   invoke it by a for loop to do the last processing by yourself.


# Function wrapper

Unless using auto-type conversion of cmdlet.cmds module, function should not
be used in pipes directly. Cmdlet provides a set of basic wrappers to wrap
function to Pipe object.

## pipe.func(generator_function)

The most basic wrapper. In Python, generator function is a function with yield
statement in it. The generator_function defined here is a Python generator
function with at least one argument. The argument is a generator object passed
from previous Pipe object. generator_function can take it as input or just
leave it. It looks like:

```python
# Generator function which use prev as input.
@pipe.func
def my_generator(prev):
    for data in prev:
        # ... Put some code to process data ...
        yield new_data
```
```python
# Generator function which ignore input.
@pipe.func
def my_generator_ignore_prev(prev):
    while True:
        # ... Generate data and break loop in some conditions. ...
        yield data
```

## pipe.map(function)

Wrap function to a mapper. The input is a normal function with at least one
argument for data input. The returned value will be passed to next
Pipe object. It looks like:

```python
@pipe.map
def my_mapper(data):
    # ... Put some code to process data ...            
    return new_data
```

Anything returned by mapper will be sent to next Pipe object. If mapper return
None, next Pipe object will receive None. That is, you can't use mapper to
filter data out. It's the job of filter function. Use pipe.filter instead.

## pipe.filter(function)

Wrap function to a filter. Filter is a function with at least one argument as
data input. Filter should return Boolean value, True or False. If True, data
from previous Pipe object is allowed to pass through. If False, data is dropped.
It looks like:

```python
@pipe.filter
def my_filter(data):
    # Handle data and check conditions.
    if you_should_not_pass:
        return False
    else:
        return True
```

## pipe.reduce(function)

Wrap function as a reducer. A reducer is a function which has at least two
arguments. The first one is used as accumulated result, the second one is
the data to be processed. A optional keyword argument *init* can be used to
specify initial value to accumulated result. It looks like:

```python
@pipe.reduce
def my_reducer(accum_result, data):
    # Calculate new accum_result according to data.
    return accum_result
```

## The usage of wrapper

Here is a example to show how to use function wrapper.

```python
from random import randint
from cmdlet.cmds import *

@pipe.func
def random_number(prev, amount):
    for i in range(amount):
        yield randint(0, 100000)

@pipe.filter
def in_range(data, lower_bound, upper_bound):
    return data >= lower_bound and data <= upper_bound

@pipe.reduce
def count(accum_result, data):
    return accum_result + 1

@pipe.map
def format_output(data, format):
    return format % data

# Generate 1000 random number and count how many of them between 100 and 500.
# Then, format the result to 'ans=%d'.
cmds = random_number(1000) | in_range(100, 500) | count(init=0) | format_output('ans=%d')

print cmds.run()
# >>> ans=40
```

If wrapped code is just a expression, following code shows another way to make
them:

```python
in_range = pipe.filter(lambda data: data >= lower_bound and data <= upper_bound)
count = pipe.reduce(lambda accum_result, data: accum_result + 1)
format_output = pipe.reduce(lambda data, format: format % data)
```

> NOTE:
> As you might already noticed, the number of argument using in piped commands
> is different from the definition of wrapped function. You should know your
> function is wrapped to a Pipe object. The function is not invoked when
> cascading pipes. It is called when using run(), result() or iteration. The
> arguments will be stored in Pipe object and append to the argument list of
> wrapped function when it is invoked.

## Auto-type conversion

If the operand of **|** operator is not a Pipe object, cmdlet will call proper
creator to convert and wrap it to a Pipe object. The data type of operand must
be registered in cmdlet. Otherwise, exception *UnregisteredPipeType* will be
raised.

cmdlet.cmds has registered some basic types by default. You can use them
directly.

| Type     | wrapper      | Description                                 |
| -------- | ------------ | ------------------------------------------- |
| type     | pipe.map     | Convert processed data to specified type    |
| function | pipe.map     | Treat function as a mapper.                 |
| method   | pipe.map     | Treat function as a mapper.                 |
| tuple    | seq          | Wrap tuple to gernator.                     |
| list     | seq          | Wrap list to gernator.                      |
| str      | sh           | Wrap string to command line and execute it. |
| unicode  | sh           | Wrap string to command line and execute it. |
| file     | fileobj      | Wrap file object for read/write operation.  |


# cmdlet.cmds utilities.

cmdlet.cmds supports some utilties for easy to use pipe functions.

TODO: describe utilities here.
