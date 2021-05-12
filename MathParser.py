MATH_SYMBOLS = ['+', '-', '*', '/', '^', '&', '|', '(', ')', '%']

def calc(ops):
    i = 0
    rm = 0
    while i < len(ops):
        op = ops[i]
        if op == '(':
            ops[i], rm = calc(ops[i+1:])
            for _ in range(rm):
                ops.pop(i+1)
        elif op == ')':
            slice_ind = i
            rm += i
            ops=ops[:slice_ind]
            break
        i += 1
    i = 0
    while i < len(ops):
        op = ops[i]
        if op == '^':
            ops[i-1] = float(ops[i-1])
            ops[i-1] = ops[i-1] ** float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        i += 1
    i = 0
    while i < len(ops):
        op = ops[i]
        if op == '*':
            ops[i-1] = float(ops[i-1])
            ops[i-1] *= float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '/':
            ops[i-1] = float(ops[i-1])
            ops[i-1] /= float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '&':
            ops[i-1] = int(ops[i-1])
            ops[i-1] &= int(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '|':
            ops[i-1] = int(ops[i-1])
            ops[i-1] |= int(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '%':
            ops[i-1] = int(ops[i-1])
            ops[i-1] %= int(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        i += 1
    i = 0
    while i < len(ops):
        op = ops[i]
        if op == '+':
            ops[i-1] = float(ops[i-1])
            ops[i-1] += float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '-':
            ops[i-1] = float(ops[i-1])
            ops[i-1] -= float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        i += 1
    if len(ops) > 1:
        return None
    return ops[0], rm+1

# will never contain spaces
def isolate(arg):
    args = []
    zero = 0
    for i in range(len(arg)):
        if arg[i] in MATH_SYMBOLS:
            if i != zero:
                args.append(arg[zero:i])
            args.append(arg[i])
            zero = i+1
    if arg[zero:]:
        args.append(arg[zero:])
    
    return args

def parse(args, searching=False):
    ops = []
    for arg in args:
        isoOps = isolate(arg)
        for op in isoOps:
            ops.append(op)
    
    return ops