import ast
import hashlib
import json
import math
from pathlib import Path

DATA = Path(__file__).parent / 'data'

def pdiv(a, b):
    d = (1e-4 if b >= 0 else -1e-4) if abs(b) < 1e-4 else b
    return max(-1e4, min(1e4, a / d))

def erf(a):
    sign = -1 if a < 0 else 1
    ax = abs(a)
    t = 1 / (1 + 0.3275911 * ax)
    poly = ((((1.061405429*t - 1.453152027)*t + 1.421413741)*t - 0.284496736)*t + 0.254829592)*t
    return sign * (1 - poly * math.exp(-ax*ax))

# Only operations used by the two imported records. Unknown operations fail closed.
OPS = {'erf': (1, erf), 'add': (2, lambda a,b: a+b), 'mul': (2, lambda a,b: a*b),
       'pdiv': (2, pdiv), 'neg': (1, lambda a: -a),
       'exp': (1, lambda a: math.exp(max(-50, min(50, a)))),
       'relu': (1, lambda a: max(0, a)),
       'sub': (2, lambda a,b: a-b), 'sq': (1, lambda a: a*a)}

MAX_TREE_DEPTH = 64
MAX_TREE_NODES = 1024

def validate_tree(root):
    """Validate tree shape and size iteratively, before recursive AST construction."""
    stack = [(root, 1)]
    count = 0
    while stack:
        node, depth = stack.pop()
        count += 1
        if count > MAX_TREE_NODES:
            raise ValueError('Tree node limit exceeded')
        if depth > MAX_TREE_DEPTH:
            raise ValueError('Tree depth limit exceeded')
        if not isinstance(node, dict):
            raise ValueError('Tree node must be an object')
        op = node.get('o')
        if op == 'var':
            if set(node) != {'o', 'n'} or node['n'] != 'x':
                raise ValueError('Only variable x is supported')
        elif op == 'const':
            if set(node) != {'o', 'v'} or isinstance(node['v'], bool):
                raise ValueError('Invalid constant')
            try:
                value = float(node['v'])
            except (TypeError, ValueError, OverflowError):
                raise ValueError('Invalid constant') from None
            if not math.isfinite(value):
                raise ValueError('Non-finite constant')
        elif isinstance(op, str) and op in OPS:
            if set(node) != {'o', 'c'}:
                raise ValueError('Invalid operator node')
            children = node['c']
            if not isinstance(children, list) or len(children) != OPS[op][0]:
                raise ValueError('Invalid operator arity')
            stack.extend((child, depth + 1) for child in children)
        else:
            raise ValueError('Unsupported operator')

def compile_tree(node):
    """Build Python AST from whitelisted operators, never from formula text."""
    validate_tree(node)
    def build(n):
        op = n['o']
        if op == 'var':
            if n.get('n') != 'x':
                raise ValueError('Only x is supported')
            return ast.Name(id='x', ctx=ast.Load())
        if op == 'const':
            v = float(n['v'])
            if not math.isfinite(v):
                raise ValueError('Non-finite constant')
            return ast.Constant(value=v)
        if op not in OPS:
            raise ValueError(f'Unsupported operator: {op}')
        arity, _ = OPS[op]
        children = n.get('c', [])
        if len(children) != arity:
            raise ValueError(f'Invalid arity: {op}')
        args = [build(c) for c in children]
        if op in ('add', 'mul'):
            return ast.BinOp(left=args[0], op=ast.Add() if op == 'add' else ast.Mult(), right=args[1])
        if op == 'neg':
            return ast.UnaryOp(op=ast.USub(), operand=args[0])
        return ast.Call(func=ast.Name(id=op, ctx=ast.Load()), args=args, keywords=[])
    expression = ast.Expression(body=ast.Lambda(
        args=ast.arguments(posonlyargs=[], args=[ast.arg(arg='x')],
                           kwonlyargs=[], kw_defaults=[], defaults=[]),
        body=build(node)))
    code = compile(ast.fix_missing_locations(expression), '<ledger>', 'eval')
    scope = {'__builtins__': {}}
    scope.update({name: fn for name, (_, fn) in OPS.items()})
    return eval(code, scope)

class Registry:
    def __init__(self):
        self.source = json.loads((DATA / 'source.json').read_text())
        self.records, self.functions = {}, {}
        for name, checksum in self.source['sha256'].items():
            raw = (DATA / f'{name}.json').read_bytes()
            if hashlib.sha256(raw).hexdigest() != checksum:
                raise ValueError(f'Source checksum mismatch: {name}')
            record = json.loads(raw)
            if record['taskId'] != name:
                raise ValueError('Task mismatch')
            self.records[name] = record
            self.functions[name] = compile_tree(record['tree'])

    def compute(self, name, x):
        x = float(x)
        if not math.isfinite(x):
            raise ValueError('Finite input required')
        result = self.functions[name](x)
        if not math.isfinite(result):
            raise ValueError('Non-finite result')
        return result

class Router:
    """Explicit tasks only: no guess about whether natural language is trivial."""
    def __init__(self, registry=None):
        self.registry = registry or Registry()

    def run(self, task):
        kind = task.get('kind')
        if kind == 'discover':
            from .discovery import discover
            return discover(task)
        if kind == 'compute':
            name = task.get('kernel')
            if name not in self.registry.records:
                return {'status': 'unsupported', 'reason': 'Unknown kernel'}
            return {'status': 'ok', 'backend': 'python-ledger', 'kernel': name,
                    'value': self.registry.compute(name, task['x']),
                    'source_commit': self.registry.source['commit']}
        if kind in ('browser', 'llm'):
            return {'status': 'unavailable', 'backend': kind,
                    'reason': 'Adapter not connected; no external action performed'}
        return {'status': 'unsupported', 'reason': 'Use compute, discover, browser or llm'}
