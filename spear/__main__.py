import argparse
import json
import sys
from .core import Router

p = argparse.ArgumentParser(description='Offline SPEAR prototype; input is a JSON task')
p.add_argument('task', help='e.g. {"kind":"compute","kernel":"silu","x":1}')
a = p.parse_args()
try:
    result = Router().run(json.loads(a.task))
except (ValueError, KeyError, TypeError, OverflowError) as e:
    print(json.dumps({'status': 'error', 'reason': str(e)}))
    sys.exit(2)
print(json.dumps(result, allow_nan=False))
if result['status'] != 'ok':
    sys.exit(1)
