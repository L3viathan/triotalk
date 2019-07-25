# Trio

programare async pentru oameni și prieteni de șarpe

> P.S. API tău e o interfața utilizator. – **Kenneth Reitz**

====

Jonathan Oberländer, [@l3viathan@mastodon.social](), [https://github.com/L3viathan]()

====

# De ce Trio

- De ce nu async.io/Twisted/curio/...?
- Ce face Trio diferit?

====

> Trio încearcă să se distingă cu un focus obsesiv asupra **utilizabilității** și **corectitudinii**. Concurrency este complicat; încercăm să facem *ușor* pentru a obține lucrurile *corect*.

====

# Ai nevoie de...

- Python relativ nou
- Cunoștințe decente de Python

====

# Nu ai nevoie de...

- Cunoștințe de asyncio
- Cunoștințe de `async`/`await`

====

# funcții async

```python
async def double(x):
    return x*2
```

====

- Trebuie să utilizați `await` pentru a apela funcția
- Puteți utiliza numai funcția `await` în interiorul funcțiilor asincrone

====

```
  _____)      _____)
 /_ ___/     /_ ___/
 / _ \       / _ \
| (_) |     | (_) |
 \___/ _____ \___/
      |_____|
```

====

```python
import trio

async def double(x):
    return 2 * x

trio.run(double, 3)  # returnează 6
```

====

```exechidden
import trio
```

```exec
async def sleepy(seconds):
    print(f"Dorm pentru {seconds} secunde")
    await trio.sleep(seconds)
    print(f"Am dormit {seconds} secunde")
```
====

```exec
async def main():
    async with trio.open_nursery() as nursery:
        for i in range(5):
            nursery.start_soon(sleepy, i)
        print("Am pornit toate sarcinile")
    print("Gata")
```

====

- Sarcini au fost programate într-o ordine diferită (poate)
- Sarcinile au fugit simultan
- `"Gata"` este imprimată _la sfarsit_.

====

# nurseries

====

Edsger W. Dijkstra (1968): Go To Statement Considered Harmful

- Primele de flux de control în limbile de programare timpurie: if, bucle, apeluri funcționale, goto (adevărat)
- Toate, ***cu excepția goto*** poate fi văzut ca un black box

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

- nu știm dacă venim înapoi acolo
- *goto* face imposibilă raționamentul

====

**Spoiler alert:** Dijkstra a câștigat

- limbile cu `goto` (C, C#, Golang) l-au îmblânzit
- eliminarea goto permite crearea de noi construcții

====
```python
with foo:
    do_stuff()
```

====
- ce s-ar întâmpla dacă sari în afară?
- ce dacă sari _înăuntru_?
====

# go

====

- declarația `go`, de asemenea cunoscut ca si `pthread_create`, `spawn`, `threading.Thread`, `asyncio.create_task`, ...

====
```
go
 |
 +---> []
 |
 V
```
====
- Este un goto în deghizare!
- Greu să te gândești (da, știu despre `join`)
- Întrerupe manipularea erorilor
- Întrerupe abstracțiune
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

- Sarcinile _trebuie_ să ruleze într-o nursery* **
- Sarcinile care au început într-o nursery sunt terminate înainte ca nursery să fie închisă.

====

Și dacă trebuie să porniți dinamic sarcinile?

====

```exec
async def starter(nursery):
    for i in range(7):
        nursery.start_soon(sleepy, i)
    print("starter gata")

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(starter, nursery)
    print("gata de tot")
```

====

- sarcinile `sleepy` sunt atașate la nursery, nu la `starter`
- `starter` poate ieși, `main` **nu** poate

====

# anulare

====

- I really think you'd be bored by this novelty by now; switching back to English
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
    data = await conn.receive_some(1024)
    await conn.send_all(data)

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(trio.serve_tcp, handler, 1234)
```
====

```exec
async def handler(conn):
    while True:
        data = await conn.receive_some(1024)
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
