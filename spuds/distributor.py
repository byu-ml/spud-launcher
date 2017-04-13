import asyncio
import asyncssh
import argparse
import itertools
from spuds import Potatoes
from spuds.free_potato import free_potatoes
from collections import OrderedDict


async def run_client(host, command):
    async with asyncssh.connect(host, known_hosts=None) as conn:
        return await conn.run(command)

async def run_multiple_clients(hosts, commands):

    # tasks = [run_client(host, 'pwd') for host in hosts]
    # results = await asyncio.gather(*tasks, return_exceptions=True)
    available = await free_potatoes(hosts)
    for comms in get_commands(commands, available):
        tasks = [run_client(h[0], 'echo "echo: ' + c + '"') for c, h in zip(comms, available)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print('Task %d failed: %s' % (i, str(result)))
            elif result.exit_status != 0:
                print('Task %d exited with status %s:' % (i, result.exit_status))
                print(result.stderr, end='')
            else:
                print('Task %d succeeded:' % i)
                print(result.stdout)
            print()
            print(75*'-')
        # update availability
        _next = await free_potatoes(hosts)
        available = await asyncio.sleep(2, _next)

    # tasks = [run_client(host[0], 'pwd') for host in available]
    # results = await asyncio.gather(*tasks, return_exceptions=True)
    #
    # for i, result in enumerate(results):
    #     if isinstance(result, Exception):
    #         print('Task %d failed: %s' % (i, str(result)))
    #     elif result.exit_status != 0:
    #         print('Task %d exited with status %s:' % (i, result.exit_status))
    #         print(result.stderr, end='')
    #     else:
    #         print('Task %d succeeded:' % i)
    #         print(result.stdout)
    #     print()
    #     print(75*'-')


def get_commands(_commands, available):
    _i = 0
    while _i < len(_commands):
        yield _commands[_i:_i + len(available)]
        _i += len(available)


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
    parser.add_argument('--dry', action='store_true', help='dry-run to show how many jobs would be dispatched')
    args = parser.parse_args()
    params = parse_params(args.params)
    # combinations are same as in insertion order
    combos = list(itertools.product(*params.values()))
    print('# of combos:', len(combos))
    # assemble as commands
    _commands = []
    for i, _combo in enumerate(combos):
        _p = args.command
        for k, v in zip(params.keys(), _combo):
            _p += ' -' + k + ' ' + str(v)
        _commands.append(_p)
        if args.dry:
            print('Job ' + str(i) + ":", _p)
    # distribute commands
    p = Potatoes()
    _hosts = p.spuds
    if not args.dry:
        asyncio.get_event_loop().run_until_complete(run_multiple_clients(_hosts, _commands))
    else:
        print("--dry run")
