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

```
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

```
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

```
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
No, the problem with the GIL is that it’s a lousy deal: we give up on using multiple cores, and in exchange we get… almost all the same challenges and mind-bending bugs that come with real parallel programming, and – to add insult to injury – pretty poor scalability. Threads in Python just aren’t that appealing.

====

# synchronization primitives (channels)

# exceptions

====
second example: spider?

