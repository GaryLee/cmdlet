# What is cmdlet?

Cmdlet provides pipe-like mechanism to cascade functions and generators. It
uses symbol(**|**) to convert function to Pipe object and cascade them. This
sequence of commands can be executed and evaluated later. Just like pipe
mechanism in Unix shell. For example:

```python
from cmdlet.cmds import *

# Create piped commands.
cmds = range(10) | pipe.filter(lambda x: x > 5) | fmt('item#%d')

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

First, we created commands and used **|** to cascade them. Then, we can execute
commands by run(), result() or iterator.

cmdlet can convert corresponding types to Pipe object automatically. In above
example, range(10) is an iterator not a Pipe object. Because second item is
a Pipe object(made by pipe.filter), it turns out first item to be converted
to a Pipe object automatically.

There are many useful utilities in cmdlet.cmds modules. They can provide a great
convenience to build up useful pipes. Here is an example:

```python
from cmdlet.cmds import *

query_topic =
    'find ./mydoc -name "*.txt" -print' |
    readline(end=10) |
    match(r'^[tT]opic:\s*(?P<topic>.+)\s*', to=dict) |
    values('topic')

for topic in query_topic:
    print topic
```

In above example, the goal is to query topic from article files. To achieve the
goal, we have to:

1. Search text files in a given folder.
2. Read first 10 lines from each file.
3. Find the line that matched 'topic: foo bar' pattern.
4. Extract the topic string.

With the utilities provided by *cmdlet.cmds*, we only need to write a few of
code. The first string which starts with 'find' is a normal shell script. It is
converted to *sh* pipe automatically and executed with system shell. The
*readline* pipe can open files whose name passed from sh pipe. *match* pipe
and *values* pipe work together to extract topic from file content.

Above example shows not only small code but also readability. It's really easy
to understand the purpose of source code.

NOTE:
> When using cmdlet's pipe mechanism, make sure one of your
> **first two pipe items** is a valid Pipe object.

There is another advantage to use cmdlet. The pipe object is evaluated when
calling result, run or iter. It implies you can reuse them. Let's modify
previous example.

```python
from cmdlet.cmds import *

# Separate from query_topic command.
extract_topic =
    readline(end=10) |
    match(r'^[tT]opic:\s*(?P<topic>.+)\s*', to=dict) |
    values('topic')

for topic in ('find ./mydoc1 -name "*.txt" -print' | extract_topic):
    print topic

for topic in ('find ../mydoc2 -name "*.md" -print' | extract_topic):
    print topic

```

# How to install

Just like other packages on PyPI. You can use pip to download and install
automatically.

```shell
$ pip install cmdlet
```

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

Function should not be used in pipes directly, unless using auto-type
conversion. Cmdlet provides a set of basic wrappers to wrap function to Pipe
object.

## pipe.func(generator_function)

The most basic wrapper. In Python, generator function is a function with yield
statement in it. The generator_function defined here is a Python generator
function with at least one argument. The first argument is a generator object
passed by previous Pipe object. generator_function can take it as input or just
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

For example:
```python
@pipe.func
def randint_generator(prev, num):
    for i in range(num):
        yield random.randint(0, 1000)

@pipe.func
def power(prev, th):
    for n in prev:
        yield n ** th

cmds = randint_generator(10) | power
ans = result(cmds)
# Equals to:
# ans = []
# for i in range(10):
#     ans.append(random.randint(0, 1000)
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

For example:
```python
@pipe.func
def randint_generator(prev, num):
    for i in range(num):
        yield random.randint(0, 1000)

@pipe.map
def power(n, th):
    return n ** th

cmds = randint_generator(10) | power
ans = result(cmds)
# Equals to:
# ans = []
# for i in range(10):
#     ans.append(random.randint(0, 1000)
```

The power pipe can also be written in this way:
```python
power = pipe.map(lambda n, th: n ** th)
```

Anything returned by mapper will be sent to next Pipe object. If mapper return
None, next Pipe object will receive None. That is, you can't use mapper to
filter data out. That's why we have pipe.filter.

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

For example:
```python
@pipe.filter
def less_than(data, thrd):
    return data < thrd

cmds = range(10) | less_than(3)
ans = result(cmds)
# Equals to:
# ans = []
# thrd = 3
# for n in range(10):
#     if n < thrd:
#          ans.append()
```

You can write filter pipe in this way:
```python
less_than = pipe.filter(lambda data, thrd: data < thrd)
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

For example:
```python
@pipe.reduce
def count_mod(accum_result, data, mod_by):
    if (data % mod_by) == 0:
        return accum_result
    else:
        return accum_result + 1

cmds = range(1000) | count_mod(10, init=0)
```

## pipe.stopper(function)

Wrap function as a stopper. Stopper is used to stop the pipe execution. It
returns true to stop the pipe execution. Return false to pass data to next.
It looks like:

```python
@pipe.stopper
def my_stopper(data):
    if check_stop_criteria(data):
        return True
    return False
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

NOTE:
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

| Type     | wrapper  | Description                                 |
| -------- | -------- | ------------------------------------------- |
| type     | pipe.map | Convert processed data to specified type    |
| function | pipe.map | Wrap function as a mapper.                  |
| method   | pipe.map | Wrap method as a mapper.                    |
| tuple    | seq      | Wrap tuple to generator.                    |
| list     | seq      | Wrap list to generator.                     |
| str      | sh       | Wrap string to command line and execute it. |
| unicode  | sh       | Wrap string to command line and execute it. |
| file     | fileobj  | Wrap file object for read/write operation.  |


# cmdlet.cmds utilities.

cmdlet.cmds has predefined some commands. Here are brief descriptions.

## Pipe commnds for iterable object.

| Command  | Description                                                |
| -------- | ---------------------------------------------------------- |
| pack     | Take N elements from pipe and group them into one element. |
| enum     | Generate (index, value) pair from previous pipe.           |
| counter  | Count the number of data from previous pipe.               |
| flatten  | Flatten the data passed from previous pipe.                |
| items    | Extract (key, value) pair from a dict-like object.         |
| seq      | Extract any iterable object.                               |
| attr     | Extract the value of given attribute from previous pipe.   |
| attrs    | Extract the value of given attributes from previous pipe.  |
| attrdict | Extract the value of given attributes from previous pipe.  |

## Pipe commands for file

| Command  | Description                               |
| -------- | ----------------------------------------- |
| stdout   | Output data from previous pipe to stdout. |
| stderr   | Output data from previous pipe to stderr. |
| readline | Read data from file line by line.         |
| fileobj  | Read/write file with pipe data.           |

## Pipe commands for shell

| Command | Description                                                                                                                                |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| sh      | Execute system shell script to handle the stdin/stdout. The data from previous pipe will be the standard input of specified shell command. |
| execmd  | Execute system shell script to handle the stdin/stdout. The data from previous pipe will be the command line to be executed.               |

## Pipe commands for strings

### Alias of string method

| Command         | Description                                       |
| --------------- | ------------------------------------------------- |
| upper           | alias of string.upper                             |
| lower           | alias of string.lower                             |
| capwords        | alias of string.capwords                          |
| capitalize      | alias of string.capitalize                        |
| lstrip          | alias of string.lstrip                            |
| rstrip          | alias of string.rstrip                            |
| strip           | alias of string.strip                             |
| expandtabs      | alias of string.expandtabs                        |
| strip           | alias of string.strip                             |
| find            | alias of string.find                              |
| fmt             | alias of % operator of string (not string.format) |
| rfind           | alias of string.rfind                             |
| count           | alias of string.count                             |
| split           | alias of string.split                             |
| rsplit          | alias of string.rsplit                            |
| swapcase        | alias of string.swapcase                          |
| translate       | alias of string.translate                         |
| ljust           | alias of string.ljust                             |
| rjust           | alias of string.rjust                             |
| center          | alias of string.center                            |
| zfill           | alias of string.zfill                             |
| replace         | alias of string.replace                           |
| join            | alias of string.join                              |
| substitute      | alias of string.Template.substitute               |
| safe_substitute | alias of string.Template.safe_substitute          |

### String split, search and match

| Command  | Description                                                    |
| -------- | -------------------------------------------------------------- |
| grep     | Grep strings with regular expression.                          |
| match    | Grep strings with regular expression and generate MatchObject. |
| wildcard | Grep strings with wildcard character.                          |
| resplit  | Split strings with regular expression.                         |
| sub      | Substitute strings with regular expression.                    |
| subn     | Substitute strings with regular expression.                    |
