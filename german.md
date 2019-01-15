# Trio

async-Programmierung für Menschen und Schlangenliebhaber

> P.S. deine API ist ein Userinterface – **Kenneth Reitz**

====

Jonathan Oberländer, [@l3viathan@mastodon.social](), [https://github.com/L3viathan](), solute

====

# Warum Trio

- Warum nicht async.io/Twisted/curio/...?
- Was macht Trio anders?

====

> Trio attempts to distinguish itself with an obsessive focus on **usability** and **correctness**. Concurrency is complicated; we try to make it *easy* to get things *right*.

> Trio versucht, durch seinen obsessiven Fokus auf **Benutzbarkeit** und **Korrektheit** herauszustechen. Nebenläufigkeit ist kompliziert; wir versuchen es *leicht* zu machen Dinge *richtig* zu machen.

====

# Du brauchst...

- Einigermaßen aktuelles Python
- Einigermaßen gutes Python-Wissen

====

# Du brauchst kein...

- Verständnis von asyncio
- Verständnis von `async`/`await`

====

# async-Funktionen

```python
async def double(x):
    return x*2
```

====

- Du musst `await` benutzen, um die Funktion aufzurufen.
- Du kannst `await` nur innerhalb von async-Funktionen benutzen.

====

```
ಠ_ಠ
```

====

```python
import trio

async def double(x):
    return 2 * x

trio.run(double, 3)  # gibt 6 zurück
```

====

```exechidden
import trio
```

```exec
async def sleepy(seconds):
    print(f"Schlafe {seconds} Sekunden")
    await trio.sleep(seconds)
    print(f"Habe {seconds} Sekunden geschlafen")
```
====

```exec
async def main():
    async with trio.open_nursery() as nursery:
        for i in range(5):
            nursery.start_soon(sleepy, i)
        print("Alle Tasks gestartet")
    print("Fertig")
```

====

- Tasks wurden (vielleicht) in einer anderen Reihenfolge geschedult
- Tasks rannen parallel
- `"Fertig"` wurde _am Ende_ ausgegeben.

====

# nurseries

====

Edsger W. Dijkstra (1968): Go To Statement Considered Harmful

- Kontrollstrukturprimitive in frühen Programmiersprachen: if, Schleifen, Funktionsaufrufe, (echtes) goto
- Alles außer goto kann als black box betrachtet werden, goto ***nicht***

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

- Wir wissen nicht, ob wir wieder hierher zurückkehren werden
- *goto* ist unanalysierbar

====

**Spoiler alert:** Dijkstra hat gewonnen

- selbst Sprachen mit `goto` (C, C#, Golang) haben es gezähmt
- Entfernung von goto erlaubt die Erfindung völlig neuer Konstrukte...

====
```python
with foo:
    do_stuff()
```

====
- Was würde passieren, wenn wir aus dem with-Block sprängen?
- Was, wenn wir _hineinsprängen_?
====

# go

====

- das `go`-Statement, auch bekannt als `pthread_create`, `spawn`, `threading.Thread`, `asyncio.create_task`, ...

====
```
go
 |
 +---> []
 |
 V
```
====
- Es ist ein getarntes goto!
- Schwer zu analysieren (ja, ich kenne `join`)
- Bricht Fehlerbehandlung
- Bricht Abstraktion
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

- *"nursery" ≈ Kindertagesstätte, Anm. d. Übers.*
- Tasks _müssen_ in Nurseries laufen* **
- Tasks, die in einer Nursery laufen, sind fertig bevor die Nursery schließt

====

Was, wenn Tasks dynamisch gestartet werden sollen?

====

```exec
async def starter(nursery):
    for i in range(7):
        nursery.start_soon(sleepy, i)
    print("starter fertig")

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(starter, nursery)
    print("Ganz fertig")
```

====

- `sleepy`-Tasks hängen an der Nursery, nicht an `starter`
- `starter` kann sich beenden, `main` **nicht**

====

# cancellation

====

- Tasks können jederzeit abgebrochen werden*
- Beispiel: Timeouts

====

```exec
async def main():
    with trio.move_on_after(3):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(sleepy, 10)
    print("Fertig")
```

====

- auch möglich: `trio.fail_after`, `trio.move_on_at`
- auch möglich: nursery.cancel_scope.cancel()

====

- Cancellations werfen eine Exception in allen Kinder-Tasks
- Cancellations sind nur an Checkpoints möglich

====

# checkpoints

====

- Stellen im Code, an denen Tasks abgebrochen werden können
- Stellen im Code, an denen Task-Switching passiert

====

- Jede Stelle, an der wir eine "echte" asynchrone Funktion `await`en, d.h. jedes `await` von trio.irgendwas
- Manueller Checkpoint: `await trio.sleep(0)`

====

# Synchronisierung

====

- `send, receive = trio.open_memory_channel(3)`
- Alternativen: `trio.Event`, `trio.CapacityLimiter`, `trio.Semaphore`, `trio.Lock`, ...

====

```exec
async def sender(chan):
    async with chan:
        for i in range(3):
            await chan.send(i)
            print(i, "geschickt")
```
====

```exec
async def receiver(chan):
    async with chan:
        async for msg in chan:
            print(msg, "empfangen")
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

# Exceptions

====

- Exceptions funktionieren einfach, und werden nie verworfen.
- "gleichzeitig" geworfene Exceptions werfen einen `trio.MultiError`.

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
    print(f"Neue Verbindung von [{ip}]:{port}")
    while True:
        data = await conn.receive_some(1024)
        print(f"[{ip}]:{port} hat Daten geschickt")
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
    print(f"Neue Verbindung von [{ip}]:{port}")
    while True:
        data = await conn.receive_some(1024)
        if not data:  # ctrl-d
            print(f"Verbindung von [{ip}]:{port} geschlossen")
            return
        print(f"[{ip}]:{port} hat Daten geschickt")
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
    print(f"Neue Verbindung von [{ip}]:{port}")
    while True:
        with trio.move_on_after(5) as scope:
            data = await conn.receive_some(1024)
            if not data:  # ctrl-d
                print(f"Verbindung von [{ip}]:{port} geschlossen")
                return
            print(f"[{ip}]:{port} hat Daten geschickt")
            await conn.send_all(data)
        if scope.cancelled_caught:
            print(f"Timeout für [{ip}]:{port}, Abbruch")
            return
```
```exechidden
async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(trio.serve_tcp, handler, 1234)
```
====

# more

- I/O: TCP, Dateisystem, Sockets, trio.subprocess, Signale
- Tasklokaler Speicher (mit `contextvars`)
- Threadunterstützung
- `trio.testing`
- `trio.hazmat`

====

- [https://vorpus.org/blog/]()
- [https://trio.readthedocs.io]()

====

# fin
