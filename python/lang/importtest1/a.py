import test
from test.b import num
from test.c import printnum1, printnum2

print 'num = ', num
num = 3
print 'num = ', num
print 'test.b.num = ', test.b.num
printnum1()
printnum2()

print
test.b.num =  4
print 'num = ', num
print 'test.b.num = ', test.b.num
printnum1()
printnum2()
