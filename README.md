# wirepickle

Effortless python remote procedure calling with pickle over [ZeroMQ](http://zeromq.org).
Allows you to expose a single class instance as an API server over every transport layer
that ZeroMQ provides.

## Quick Setup

Install wirepickle using your favorite package manager:

```bash
$ pip install wirepickle
```

### Server

Next, on your server, annotate the methods you want to expose with the `@expose` decorator:

```python
from wirepickle.server import expose, Server

class Foo:
    @expose('bar')
    def bar(self):
        print('bar')
        return 0

    @expose('baz')
    def baz(self, arg1, kwarg1='baz'):
        print(kwarg1)
        return self.bar() + arg1
```

Note that you can return anything that can be pickled as a return value,
and that stdout will be mirrored to the client.

Then, pass an instance of the class to the `Server` constructor to create the server.
To start listening, call the `Server#listen()` method on the constructed server with
a bind URI:

```
if __name__ == '__main__':
    instance = Foo()

    Server(instance).listen('tcp://*:12345')
```

### Client

Simply pass a URI to connect to and start using the methods.

```python
from wirepickle.client import Client

foo = Client('tcp://127.0.0.1:12345')

foo.bar()
```

If desired, you can pass a `timeout` kwarg to the `Client` constructor:

```python
foo = Client('tcp://127.0.0.1:12345', timeout=1_000) # milliseconds
```
