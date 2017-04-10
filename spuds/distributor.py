import asyncio
import asyncssh
import re
from spuds import Potatoes


async def run_client(host, command):
    async with asyncssh.connect(host, known_hosts=None) as conn:
        return await conn.run(command)

async def run_multiple_clients():
    # Put your lists of hosts here
    potatoes = Potatoes()
    hosts = potatoes.all

    tasks = [run_client(host, 'hostname && uptime') for host in hosts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # results, pending = await asyncio.wait(tasks)

    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print('Task %d failed: %s' % (i, str(result)))
        elif result.exit_status != 0:
            print('Task %d exited with status %s:' % (i, result.exit_status))
            print(result.stderr, end='')
        else:
            print('Task %d succeeded:' % i)
            print(parse_load(result.stdout), end='')
        print()
        print(75*'-')


def parse_load(line):
    """Parses the load from a line of uptime output"""
    if 'load average' in line:
        samples = [float(val.replace(',', '')) for val in line.split()[-3:]]
        return sum(samples) / len(samples)
    else:
        return 0

asyncio.get_event_loop().run_until_complete(run_multiple_clients())
