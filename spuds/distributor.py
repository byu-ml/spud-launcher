import asyncio
import asyncssh
import argparse
import itertools
from spuds import Potatoes
from collections import OrderedDict


async def run_client(host, command):
    async with asyncssh.connect(host, known_hosts=None) as conn:
        return await conn.run(command)

async def run_multiple_clients():
    # Put your lists of hosts here
    potatoes = Potatoes()
    hosts = potatoes.all

    tasks = [run_client(host, 'hostname && uptime') for host in hosts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print('Task %d failed: %s' % (i, str(result)))
        elif result.exit_status != 0:
            print('Task %d exited with status %s:' % (i, result.exit_status))
            print(result.stderr, end='')
        else:
            print('Task %d succeeded:' % i)
        print()
        print(75*'-')


def parse_params(params):
    result = OrderedDict()
    for _p in params:
        result[_p[0]] = _p[1:]
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='the base command to run')
    parser.add_argument('--params', '-p', action='append', nargs='+',
                        help='specifies a parameter - multiple values may be used, and may be used more than once')
    args = parser.parse_args()
    params = parse_params(args.params)
    print(args.command, params, params.values())
    # combinations are same as in insertion order
    combos = list(itertools.product(*params.values()))
    print('# of combos:', len(combos))
    #asyncio.get_event_loop().run_until_complete(run_multiple_clients())
