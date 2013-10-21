# -*- coding: UTF-8 -*-
import sys
import random

def init_arr(num):
    return [31, -41, 59, 26, -53, 58, 97, -93, -23, 84]
    #return [random.randint(-100, 100) for i in xrange(num)]

def  maxsum1(arr):
    n = len(arr)
    maxsofar = 0
    for i in range(n):
        for j in range(i, n):
            sum = 0
            for k in range(i, j+1):
                sum += arr[k]
            maxsofar = max(maxsofar, sum)
    return maxsofar

def  maxsum2(arr):
    n = len(arr)
    maxsofar = 0
    for i in range(n):
        sum = 0
        for j in range(i, n):
            sum += arr[j]
            maxsofar = max(maxsofar, sum)
    return maxsofar

def maxsum3(arr):
    return maxsum3_internal(arr, 0, len(arr) - 1)

def maxsum3_internal(arr, l, u):
    if (l > u):
        return 0
    if (l == u):
        return max(0, arr[l])

    m = (l + u) / 2

    lmax = sum = 0
    for i in reversed(range(l, m + 1)):
        sum += arr[i]
        lmax = max(lmax, sum)

    rmax = sum = 0
    for i in range(m+1, u+1):
        sum += arr[i]
        rmax = max(rmax, sum)

    return max(lmax+rmax, maxsum3_internal(arr, l, m), maxsum3_internal(arr, m+1, u))

def maxsum4(arr):
    n = len(arr)
    maxsofar = 0
    maxendinghere = 0
    for i in range(n):
        maxendinghere = max(maxendinghere+arr[i], 0)
        maxsofar = max(maxsofar, maxendinghere)
    return maxsofar

arr=init_arr(500);
print arr

if __name__ == '__main__':
    from timeit import Timer

    t1=Timer("n = maxsum1(arr)\nprint n","from __main__ import arr, maxsum1")
    print t1.timeit(number=1)
    print t1.repeat(repeat=3,number=1)

    t2=Timer("n = maxsum2(arr)\nprint n","from __main__ import arr, maxsum2")
    print t2.timeit(number=1)
    print t2.repeat(repeat=3,number=1)

    t3=Timer("n = maxsum3(arr)\nprint n","from __main__ import arr, maxsum3")
    print t3.timeit(number=1)
    print t3.repeat(repeat=3,number=1)

    t4=Timer("n = maxsum4(arr)\nprint n","from __main__ import arr, maxsum4")
    print t4.timeit(number=1)
    print t4.repeat(repeat=3,number=1)


    import profile
    # ncalls  函数的被调用次数
    # tottime  函数总计运行时间，除去函数中调用的函数运行时间
    # percall  函数运行一次的平均时间，等于tottime/ncalls
    # cumtime  函数总计运行时间，含调用的函数运行时间
    # percall  函数运行一次的平均时间，等于cumtime/ncalls
    # filename:lineno(function)  函数所在的文件名，函数的行号，函数名
    profile.run("maxsum1(arr)")
    profile.run("maxsum2(arr)")
    profile.run("maxsum3(arr)")
    profile.run("maxsum4(arr)")

