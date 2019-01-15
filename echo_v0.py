import trio

async def handler(conn):
    data = await conn.receive_some(1024)
    await conn.send_all(data)

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(trio.serve_tcp, handler, 1234)

trio.run(main)
