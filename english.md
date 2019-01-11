# Trio

async programming for humans and snake people

> P.S. your API is a user interface – **Kenneth Reitz**

====

Jonathan Oberländer, [@l3viathan@mastodon.social](), [https://github.com/L3viathan](), solute

====

# Why Trio

- Why not async.io/Twisted/curio/...?
- What makes Trio different?

====

> Trio attempts to distinguish itself with an obsessive focus on **usability** and **correctness**. Concurrency is complicated; we try to make it *easy* to get things *right*.

====

# You need...

- Reasonably up to date Python
- Decent knowledge of Python

====

# You don't need...

- Understanding of asyncio
- Understanding of `async`/`await`

====

# async functions

```python
async def double(x):
    return x*2
```

====

- You have to use `await` to call the function
- You can only use `await` inside asynchronous functions

====

```
ಠ_ಠ
```

====

```python
import trio

async def double(x):
    return 2 * x

trio.run(double, 3)  # returns 6
```

====

```exechidden
import trio
```

```exec
async def sleepy(seconds):
    print(f"Sleeping for {seconds} seconds")
    await trio.sleep(seconds)
    print(f"Slept {seconds} seconds")
```
====

```exec
async def main():
    async with trio.open_nursery() as nursery:
        for i in range(5):
            nursery.start_soon(sleepy, i)
        print("Started all tasks")
    print("All done")
```

====

- Tasks got scheduled in different order (maybe)
- Tasks ran concurrently
- `"All done"` gets printed _at the end_.

====

# nurseries

====

Edsger W. Dijkstra (1968): Go To Statement Considered Harmful

- Control flow primitives in early programming languages: if, loops, function calls, (real) goto
- all except goto can be seen as black boxes, goto ***can not***

====

```
   if       loop
   |          |<--\
/--+--\       []  |
|     |       +---/
[]    []      |
\--+--/       V
   |
   V
```
====
```
fn call   sequential
|            |
\-->[]       |
    /        |
/--/         |
|            |
V            V
```
====
```
goto
 |
 \---> []
```

====

- no idea if we will return there
- *goto* makes it impossible to reason about

====

**Spoiler alert:** Dijkstra won

- even languages with `goto` (C, C#, Golang) have tamed it
- removal of goto allows new constructs to get spawned...

====
```python
with foo:
    do_stuff()
```

====
- what would happen if we jumped out of the with block?
- what if we jumped _inside_?
====

# go

====

- the `go` statement, also known as `pthread_create`, `spawn`, `threading.Thread`, `asyncio.create_task`, ...

====
```
go
 |
 +---> []
 |
 V
```
====
- It's a goto in disguise!
- Hard to reason about (yes, I know about `join`)
- Breaks error handling
- Breaks abstraction
====
```python
with open(some_file) as f:
    asyncio.create_task(do_something(f))
    ...
```

====
Nathaniel J. Smith (2018): Go Statement Considered Harmful

====
```
      nursery
         |
    /----+----\
    |    |    |
    []   []   []
    |    |    |
    \----+----/
         |
         V
```
====

```python
async with trio.open_nursery() as nursery:
    nursery.start_soon(...)
    ...
```

====

- Tasks _have to_ run in nurseries* **
- Tasks started in a nursery are done before the nursery is closed.

====

What if you have to start tasks dynamically?

====

```exec
async def starter(nursery):
    for i in range(7):
        nursery.start_soon(sleepy, i)
    print("starter done")

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(starter, nursery)
    print("all done")
```

====

- `sleepy` tasks get attached to the nursery, not to `starter`
- `starter` can quit, `main` can **not**

====

# cancellation

====

- tasks can be cancelled at any time*
- example: timeouts

====

```exec
async def main():
    with trio.move_on_after(3):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(sleepy, 10)
    print("All done")
```

====

- also possible: `trio.fail_after`, `trio.move_on_at`
- also possible: nursery.cancel_scope.cancel()

====

- Cancellations raise an exception inside all child tasks
- Cancellations are only possible at checkpoints

====

# checkpoints

====

- places in the code where tasks can get cancelled
- places in the code where task switching happens

====

- any place where we `await` a "true" asynchronous function, i.e. any `await`ing of trio.something
- Manually inserting a checkpoint: `await trio.sleep(0)`

====

# Synchronization

====

- `send, receive = trio.open_memory_channel(3)`
- alternatives: `trio.Event`, `trio.CapacityLimiter`, `trio.Semaphore`, `trio.Lock`, ...

====

```exec
async def sender(chan):
    async with chan:
        for i in range(3):
            await chan.send(i)
            print("sent", i)
```
====

```exec
async def receiver(chan):
    async with chan:
        async for msg in chan:
            print("received", msg)
```

====

```exec
async def main():
    async with trio.open_nursery() as nursery:
        send, receive = trio.open_memory_channel(2)
        nursery.start_soon(sender, send)
        await trio.sleep(2)
        nursery.start_soon(receiver, receive)
```

====

# exceptions

====

- exceptions just work properly, and never get thrown away.
- "simultanously" raised exceptions raise a `trio.MultiError`.

====

# DEMO

====

```exec
async def handler(conn):
    while True:
        data = await conn.receive_some(1024)
        await conn.send_all(data)

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(trio.serve_tcp, handler, 1234)
```
====

```exec
async def handler(conn):
    ip, port, *_ = conn.socket.getpeername()
    print(f"[{ip}]:{port} opened connection")
    while True:
        data = await conn.receive_some(1024)
        print(f"[{ip}]:{port} sent data")
        await conn.send_all(data)
```
```exechidden
async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(trio.serve_tcp, handler, 1234)
```
====

```exec
async def handler(conn):
    ip, port, *_ = conn.socket.getpeername()
    print(f"[{ip}]:{port} opened connection")
    while True:
        data = await conn.receive_some(1024)
        if not data:  # ctrl-d
            print(f"connection closed from [{ip}]:{port}, exiting")
            return
        print(f"[{ip}]:{port} sent data")
        await conn.send_all(data)
```
```exechidden
async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(trio.serve_tcp, handler, 1234)
```
====

```exec
async def handler(conn):
    ip, port, *_ = conn.socket.getpeername()
    print(f"[{ip}]:{port} opened connection")
    while True:
        with trio.move_on_after(5) as scope:
            data = await conn.receive_some(1024)
            if not data:  # ctrl-d
                print(f"connection closed from [{ip}]:{port}, exiting")
                return
            print(f"[{ip}]:{port} sent data")
            await conn.send_all(data)
        if scope.cancelled_caught:
            print(f"timeout for [{ip}]:{port}, exiting")
            return
```
```exechidden
async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(trio.serve_tcp, handler, 1234)
```
====

# more

- I/O: TCP, file system, sockets, subprocesses, signals
- task-local storage (with `contextvars`)
- thread support
- `trio.testing`
- `trio.hazmat`

====

- [https://vorpus.org/blog/]()
- [https://trio.readthedocs.io]()

====

# fin
