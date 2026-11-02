import sys
import re
import time
import os

# ========== D.RAMOS LEXER ==========
TOKEN_SPEC = [
    ('COMMENT', r'#.*'),
    ('STRING', r'"[^"\\]*(\\.[^"\\]*)*"'),
    ('NUMBER', r'\d+'),
    ('ID', r'[A-Za-z_]\w*'),
    ('OP', r'[+\-*/%=<>!]+'),
    ('LBRACK', r'\['),
    ('RBRACK', r'\]'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('COMMA', r','),
    ('COLON', r':'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.'),
]
tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)
keywords = {
    'SHOW', 'IF', 'ELSE', 'WHILE', 'FOR', 'DO', 'RETURN', 
    'LEN', 'PUSH', 'POP', 'KEYS', 'IN', 'END', 'AND', 'OR', 'NOT'
}

def tokenize(code):
    tokens = []
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        val = mo.group()
        if kind in ('SKIP', 'COMMENT'):
            continue
        if kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected token error: {val}')
        if kind == 'ID' and val.upper() in keywords:
            kind = val.upper()
        if kind == 'STRING':
            val = bytes(val[1:-1], "utf-8").decode("unicode_escape")
        tokens.append((kind, val))
    tokens.append(('EOF', ''))
    return tokens

# ========== D.RAMOS PARSER ==========
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return ('EOF', '')

    def eat(self, kind):
        if self.current()[0] == kind:
            self.pos += 1
            return True
        return False

    def parse_program(self):
        stmts = []
        while self.current()[0] != 'EOF':
            if self.current()[0] == 'NEWLINE':
                self.eat('NEWLINE')
                continue
            stmts.append(self.parse_stmt())
        return ('program', stmts)

    def parse_stmt(self):
        kind, val = self.current()
        if kind == 'SHOW':
            self.eat('SHOW')
            expr = self.parse_expr()
            return ('show', expr)
        elif kind == 'IF':
            self.eat('IF')
            cond = self.parse_expr()
            self.eat('COLON')
            body = self.parse_block()
            else_body = []
            if self.current()[0] == 'ELSE':
                self.eat('ELSE')
                self.eat('COLON')
                else_body = self.parse_block()
            self.eat('END')
            return ('if', cond, body, else_body)
        elif kind == 'WHILE':
            self.eat('WHILE')
            cond = self.parse_expr()
            self.eat('COLON')
            body = self.parse_block()
            self.eat('END')
            return ('while', cond, body)
        elif kind == 'FOR':
            self.eat('FOR')
            var = self.current()[1]
            self.eat('ID')
            self.eat('IN')
            iterable = self.parse_expr()
            self.eat('COLON')
            body = self.parse_block()
            self.eat('END')
            return ('for', var, iterable, body)
        elif kind == 'DO':
            self.eat('DO')
            name = self.current()[1]
            self.eat('ID')
            params = []
            while self.current()[0] == 'ID':
                params.append(self.current()[1])
                self.eat('ID')
            self.eat('COLON')
            body = self.parse_block()
            self.eat('END')
            return ('do', name, params, body)
        elif kind == 'RETURN':
            self.eat('RETURN')
            expr = self.parse_expr()
            return ('return', expr)
        elif kind == 'ID':
            next_kind, _ = self.peek(1)
            if next_kind == 'OP' and self.peek(1)[1] == '=':
                name = val
                self.eat('ID')
                self.eat('OP')
                expr = self.parse_expr()
                return ('assign', name, expr)
            elif next_kind == 'LBRACK':
                name = val
                saved_pos = self.pos
                self.eat('ID')
                self.eat('LBRACK')
                idx = self.parse_expr()
                if self.eat('RBRACK') and self.current()[0] == 'OP' and self.current()[1] == '=':
                    self.eat('OP')
                    expr = self.parse_expr()
                    return ('sub_assign', name, idx, expr)
                self.pos = saved_pos
        expr = self.parse_expr()
        return ('expr_stmt', expr)

    def parse_block(self):
        stmts = []
        while self.current()[0] not in ('EOF', 'END', 'ELSE'):
            if self.current()[0] == 'NEWLINE':
                self.eat('NEWLINE')
                continue
            stmts.append(self.parse_stmt())
        return stmts

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.current()[0] == 'OR':
            self.eat('OR')
            right = self.parse_and()
            left = ('binop', 'OR', left, right)
        return left

    def parse_and(self):
        left = self.parse_comp()
        while self.current()[0] == 'AND':
            self.eat('AND')
            right = self.parse_comp()
            left = ('binop', 'AND', left, right)
        return left

    def parse_comp(self):
        left = self.parse_add()
        if self.current()[0] == 'OP' and self.current()[1] in ('>', '<', '==', '!=', 'IN'):
            op = self.current()[1]
            self.eat('OP')
            right = self.parse_add()
            return ('binop', op, left, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.current()[0] == 'OP' and self.current()[1] in ('+', '-'):
            op = self.current()[1]
            self.eat('OP')
            right = self.parse_mul()
            left = ('binop', op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.current()[0] == 'OP' and self.current()[1] in ('*', '/', '%'):
            op = self.current()[1]
            self.eat('OP')
            right = self.parse_unary()
            left = ('binop', op, left, right)
        return left

    def parse_unary(self):
        if self.current()[0] == 'NOT':
            self.eat('NOT')
            operand = self.parse_unary()
            return ('unary', 'NOT', operand)
        return self.parse_atom()

    def parse_atom(self):
        kind, val = self.current()
        if kind == 'NUMBER':
            self.eat('NUMBER')
            return ('num', int(val))
        if kind == 'STRING':
            self.eat('STRING')
            return ('str', val)
        if kind == 'LBRACK':
            self.eat('LBRACK')
            elems = []
            if self.current()[0] != 'RBRACK':
                elems.append(self.parse_expr())
                while self.eat('COMMA'):
                    elems.append(self.parse_expr())
            self.eat('RBRACK')
            return ('list', elems)
        if kind == 'LBRACE':
            self.eat('LBRACE')
            pairs = {}
            if self.current()[0] != 'RBRACE':
                key = self.parse_expr()
                self.eat('COLON')
                val = self.parse_expr()
                pairs[key] = val
                while self.eat('COMMA'):
                    key = self.parse_expr()
                    self.eat('COLON')
                    val = self.parse_expr()
                    pairs[key] = val
            self.eat('RBRACE')
            return ('dict', pairs)
        if kind in ('LEN', 'KEYS', 'PUSH', 'POP'):
            self.eat(kind)
            self.eat('LPAREN')
            if kind == 'PUSH':
                lst = self.parse_expr()
                self.eat('COMMA')
                val = self.parse_expr()
                self.eat('RPAREN')
                return ('push', lst, val)
            expr = self.parse_expr()
            self.eat('RPAREN')
            return (kind.lower(), expr)
        if kind == 'ID':
            name = val
            self.eat('ID')
            if self.eat('LPAREN'):
                args = []
                if self.current()[0] != 'RPAREN':
                    args.append(self.parse_expr())
                    while self.eat('COMMA'):
                        args.append(self.parse_expr())
                self.eat('RPAREN')
                return ('call', name, args)
            elif self.eat('LBRACK'):
                idx = self.parse_expr()
                self.eat('RBRACK')
                return ('index', name, idx)
            return ('var', name)
        if self.eat('LPAREN'):
            expr = self.parse_expr()
            self.eat('RPAREN')
            return expr
        raise SyntaxError(f'Unexpected token format: {val}')

# ========== D.RAMOS INTERPRETER ==========
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.env = [{}]
        self.functions = {}

    def push_scope(self): self.env.append({})
    def pop_scope(self): self.env.pop()
    def set_var(self, name, val): self.env[-1][name] = val
    def get_var(self, name):
        for scope in reversed(self.env):
            if name in scope: return scope[name]
        raise NameError(f'Variable "{name}" is not defined.')

    def eval(self, node):
        t = node[0]
        if t == 'program':
            for stmt in node[1]: self.eval(stmt)
        elif t == 'expr_stmt':
            return self.eval(node[1])
        elif t == 'assign':
            self.set_var(node[1], self.eval(node[2]))
        elif t == 'sub_assign':
            self.get_var(node[1])[self.eval(node[2])] = self.eval(node[3])
        elif t == 'show':
            print(self.eval(node[1]))
        elif t in ('num', 'str'):
            return node[1]
Use code with caution.
elif t == 'list':
return [self.eval(e) for e in node[1]]
elif t == 'dict':
return {self.eval(k): self.eval(v) for k, v in node[1].items()}
elif t == 'var':
return self.get_var(node[1])
elif t == 'index':
return self.get_var(node[1])[self.eval(node[2])]
elif t == 'len':
return len(self.eval(node[1]))
elif t == 'keys':
return list(self.eval(node[1]).keys())
elif t == 'push':
lst = self.eval(node[1])
lst.append(self.eval(node[2]))
return lst
elif t == 'pop':
return self.eval(node[1]).pop()
elif t == 'unary' and node[1] == 'NOT':
return not self.eval(node[2])
elif t == 'binop':
op = node[1]
if op == 'AND': return bool(self.eval(node[2])) and bool(self.eval(node[3]))
if op == 'OR': return bool(self.eval(node[2])) or bool(self.eval(node[3]))
a, b = self.eval(node[2]), self.eval(node[3])
ops = {
'+': lambda: a+b, '-': lambda: a-b, '': lambda: ab, '%': lambda: a%b,
'/': lambda: a//b if isinstance(a,int) and isinstance(b,int) else a/b,
'>': lambda: a>b, '<': lambda: a<b, '==': lambda: a==b, '!=': lambda: a!=b, 'IN': lambda: a in b
}
return opsop
elif t == 'if':
for s in (node[2] if self.eval(node[1]) else node[3]): self.eval(s)
elif t == 'while':
while self.eval(node[1]):
for s in node[2]: self.eval(s)
elif t == 'for':
for item in self.eval(node[2]):
self.set_var(node[1], item)
for s in node[3]: self.eval(s)
elif t == 'do':
self.functions[node[1]] = (node[2], node[3])
elif t == 'call':
if node[1] in self.functions:
params, body = self.functions[node[1]]
args = [self.eval(a) for a in node[2]]
self.push_scope()
for p, a in zip(params, args): self.set_var(p, a)
try:
for s in body: self.eval(s)
except ReturnException as e: return e.value
finally: self.pop_scope()
return None
raise NameError(f'Function undefined: {node[1]}')
elif t == 'return':
raise ReturnException(self.eval(node[1]))

========== 4-SECOND ANCHOR SPLASH SCREEN ==========

def show_splash():
os.system('cls' if os.name == 'nt' else 'clear')
splash = """
\033[94m==================================================
▓█████▄   ██▀███   ▄▄▄       ███▄ ▄███▓ ▒█████    ██████
▒██▀ ██▌ ▓██ ▒ ██▒▒████▄    ▓██▒▀█▀ ██▒▒██▒  ██▒▒██    ▒
░██   █▌ ▓██ ░▄█ ▒▒██  ▀█▄  ▓██    ▓██░▒██░  ██▒░ ▓██▄
░▓█▄   ▌ ▓██▀▀█▄  ░██▄▄▄▄██ ▒██    ▒██ ▒██   ██░  ▒   ██▒
░▒████▓  ░██▓ ▒██▒ ▓█   ▓██▒▒██    ░██▒░ ████▓▒░▒██████▒▒
▒▒▓  ▒  ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▒    ░ ▒░░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░
░ ▒  ▒    ░▒ ░ ▒░  ▒   ▒▒ ░░ ░    ░  ░  ░ ▒ ▒░ ░ ░▒  ░ ░
░ ░  ░    ░░   ░   ░   ▒   ░      ░   ░ ░ ░ ▒  ░  ░  ░
░        ░           ░  ░       ░       ░ ░        ░
C  O  R  P  O  R  A  T  I  O  N
==================================================\033[0m
"""
print(splash)
steps = ["Initializing Core Core Modules...", "Loading Lexer Maps...", "Syncing Scope Environments...", "Ready!"]
for i, step in enumerate(steps):
print(f" [\033[92m*\033[0m] {step}")
time.sleep(1.0) # Matches exactly 4 seconds split across initialization pipelines
os.system('cls' if os.name == 'nt' else 'clear')
def run_file(filename):
with open(filename, 'r', encoding='utf-8') as f: code = f.read()
tokens = tokenize(code)
ast = Parser(tokens).parse_program()
Interpreter().eval(ast)
def run_repl():
print("D.RAMOS Interactive REPL Terminal Console")
print("Type your statements below. Type 'exit' to terminate session.\n")
interp = Interpreter()
while True:
try:
line = input("dramos> ").strip()
if line.lower() == 'exit': break
if not line: continue
if line.endswith(':'):
block_lines = [line]
while True:
next_line = input("... ").strip()
block_lines.append(next_line)
if next_line == 'END': break
line = "\n".join(block_lines)
tokens = tokenize(line)
ast = Parser(tokens).parse_program()
for stmt in ast[1]:
res = interp.eval(stmt)
if stmt[0] == 'expr_stmt' and res is not None: print(repr(res))
except Exception as e:
print(f"Error: {e}")
if name == 'main':
show_splash() # Automatically fires up the 4-second animated introduction window
if len(sys.argv) > 1: run_file(sys.argv[1])
else: run_repl()