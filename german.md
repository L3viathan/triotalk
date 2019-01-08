# Trio

async-Programmierung für Menschen und Schlangenmenschen

> P.S. deine API ist ein User-Interface — **Kenneth Reitz**

----

Jonathan Oberländer, [@l3viathan@mastodon.social](), [https://github.com/L3viathan](), solute

====

# Warum Trio

- Warum nicht async.io/Twisted/curio/...?
- Was macht Trio anders?

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

- Tasks _have to_ run in nurseries* **
- Tasks started in a nursery are done before the nursery is closed.
