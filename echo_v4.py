import trio

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

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(trio.serve_tcp, handler, 1234)

trio.run(main)
