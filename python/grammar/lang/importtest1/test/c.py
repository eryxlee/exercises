from b import num

def printnum1():
    print 'printnum1: num = ', num

def printnum2():
    from b import num
    print 'printnum2: num(re-import) = ', num
