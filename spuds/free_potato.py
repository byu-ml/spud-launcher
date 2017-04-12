import asyncio
import asyncssh
import argparse
from spuds import Potatoes


async def get_load(host):
    async with asyncssh.connect(host, known_hosts=None) as conn:
        return await conn.run('uptime')

async def free_potatoes(hosts, limit=4.):
    tasks = [get_load(host) for host in hosts]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    results = []

    for i, result in enumerate(responses):
        available = False
        r = {'host': hosts[i], 'message': None, 'load': 0}
        if isinstance(result, Exception):
            r['message'] = 'Task %d failed: %s' % (i, str(result))
        elif result.exit_status != 0:
            r['message'] = 'Task %d exited with status %s: %s' % (i, result.exit_status, result.stderr)
        else:
            r['message'] = 'Task %d succeeded:' % i
            value = parse_load(result)
            if value <= limit:
                available = True
                r['load'] = value
        if available:
            results.append(r)
    return sorted(results, key=lambda _r: _r['load'])


def parse_load(result):
    """Parses the load from a line of uptime output"""
    if hasattr(result, 'stdout') and 'load average' in result.stdout:
        samples = [float(val.replace(',', '')) for val in result.stdout.split()[-3:]]
        return sum(samples) / len(samples)
    else:
        return 0


parser = argparse.ArgumentParser(description='returns a sorted list with the most available potatoes')


if __name__ == "__main__":
    args = parser.parse_args()
    # for now hard code to all potatoes
    p = Potatoes()
    hosts = p.all
    r = asyncio.get_event_loop().run_until_complete(free_potatoes(hosts))
    print(r)
