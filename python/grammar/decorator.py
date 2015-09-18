# -*- coding: utf-8 -*-

import functools


def testcase_1():
    """基本decorator的使用，decorator之后名字，docstring的变化。"""

    class decorator(object):
        """decorator docstring"""

        def __init__(self, f):
            self.f = f

        def __call__(self):
            print("Entering", self.f.__name__)
            self.f()
            print("Exited", self.f.__name__)

    def my_test():
        """test docstring"""
        print("inside my_test()")

    print("=" * 50 + "     testcase_1     " + "=" * 50)
    my_test()
    assert my_test.__name__ == 'my_test'
    assert my_test.__doc__ == 'test docstring'
    print("=" * 120)

    @decorator
    def my_test():
        """test docstring"""
        print("inside my_test()")

    my_test()
    assert my_test.__class__.__name__ == 'decorator'
    assert my_test.__class__.__doc__ == 'decorator docstring'
    print("=" * 120)


def testcase_2():
    """采用functools工具修正名字，docstring。注意，这里update_wrapper的用法。"""

    class decorator(object):
        """decorator docstring"""

        def __init__(self, f):
            self.f = f
            functools.update_wrapper(self, f)

        def __call__(self):
            print("Entering", self.f.__name__)
            self.f()
            print("Exited", self.f.__name__)

    @decorator
    def my_test():
        """test docstring"""
        print("inside my_test()")

    print("=" * 50 + "     testcase_2     " + "=" * 50)
    my_test()
    assert my_test.__name__ == 'my_test'
    assert my_test.__doc__ == 'test docstring'
    print("=" * 120)


def testcase_3():
    """带参数的decorator的类写法。"""

    class decorator(object):
        def __init__(self, arg1, arg2, arg3):
            """带参数的decorator将不从__init__方法传递被装饰对象。"""
            print("Inside __init__()")
            self.arg1 = arg1
            self.arg2 = arg2
            self.arg3 = arg3

        def __call__(self, f):
            """被装饰对象从__call__方法传入。该方法只能有这一个值。"""
            print("Inside __call__()")

            def wrapped_f(*args):
                print("Inside wrapped_f()")
                print("Decorator arguments:", self.arg1, self.arg2, self.arg3)
                f(*args)
                print("After f(*args)")

            return wrapped_f

    @decorator("hello", "world", 42)
    def say_hello(a1, a2, a3, a4):
        print('say_hello arguments:', a1, a2, a3, a4)

    print("=" * 50 + "     testcase_3     " + "=" * 50)
    say_hello("say", "hello", "argument", "list")
    print("=" * 120)


def testcase_4():
    """带参数的decorator的方法写法。"""

    def decorator(arg1, arg2, arg3):
        def wrap(f):
            print("Inside wrap()")

            def wrapped_f(*args):
                """wrapped"""
                print("Inside wrapped_f()")
                print("Decorator arguments:", arg1, arg2, arg3)
                f(*args)
                print("After f(*args)")

            return wrapped_f

        return wrap

    @decorator("hello", "world", 42)
    def say_hello(a1, a2, a3, a4):
        print('say_hello arguments:', a1, a2, a3, a4)

    print("=" * 50 + "     testcase_4     " + "=" * 50)
    say_hello("say", "hello", "argument", "list")
    assert say_hello.__name__ == 'wrapped_f'
    assert say_hello.__doc__ == 'wrapped'
    print("=" * 120)


def testcase_5():
    """将名字和docstring传回来。"""

    def decorator(arg1, arg2, arg3):
        def wrap(f):
            print("Inside wrap()")

            @functools.wraps(f)
            def wrapped_f(*args):
                """wrapped"""
                print("Inside wrapped_f()")
                print("Decorator arguments:", arg1, arg2, arg3)
                f(*args)
                print("After f(*args)")

            return wrapped_f

        return wrap

    @decorator("hello", "world", 42)
    def say_hello(a1, a2, a3, a4):
        """hello"""
        print('say_hello arguments:', a1, a2, a3, a4)

    print("=" * 50 + "     testcase_5     " + "=" * 50)
    say_hello("say", "hello", "argument", "list")
    assert say_hello.__name__ == 'say_hello'
    assert say_hello.__doc__ == 'hello'
    print("=" * 120)


def testcase_6():
    """给类使用的decorator，注意这里的wrap方式，wrap的是实例，而不是类，而且不能传入updated。"""

    def decorator(cls):
        class Wrapper(object):
            def __init__(self, *args, **kwargs):
                self.cls = cls
                functools.update_wrapper(self, cls, assigned=('__module__', '__name__', '__doc__'), updated=())
                self.instance = cls(*args, **kwargs)

            def __getattr__(self, attr):
                print('in method' + attr)
                return getattr(self.instance, attr)

        return Wrapper

    @decorator
    class MyTest(object):
        """test docstring"""

        def func(self):
            print('hello from func()')

    print("=" * 50 + "     testcase_6     " + "=" * 50)
    test = MyTest()
    assert test.__doc__ == "test docstring"
    assert test.__name__ == "MyTest"
    test.func()
    print("=" * 120)


def testcase_7():
    """给类使用的decorator，同时这个decorator也是一个类。"""

    class decorator(object):
        def __init__(self, cls):
            self.cls = cls
            self.__doc__ = cls.__doc__

        def __call__(self, *args, **kws):
            self.target_instance = self.cls(*args, **kws)
            return self  # 返回tracer的一个实例

        def __getattr__(self, attr):
            print 'tracing {0} from class: {1}'.format(attr, self.cls.__name__)
            return getattr(self.target_instance, attr)

    @decorator
    class MyTest(object):
        """test docstring"""

        def func(self):
            print('hello from func()')

    print("=" * 50 + "     testcase_7     " + "=" * 50)
    test = MyTest()
    assert test.__doc__ == "test docstring"
    test.func()
    print("=" * 120)


def testcase_8():
    """类的decorator，可以指定部分函数被装饰"""
    def class_decorator(*method_names):
        def method_decorator(fn):
            """Example of a method decorator"""
            def decorator(*args, **kwargs):
                print("\tInside the decorator")
                return fn(*args, **kwargs)

            return decorator

        def class_rebuilder(cls):
            """The class decorator example"""

            class NewClass(cls):
                """This is the overwritten class"""

                def __getattribute__(self, attr_name):
                    obj = super(NewClass, self).__getattribute__(attr_name)
                    if hasattr(obj, '__call__') and attr_name in method_names:
                        return method_decorator(obj)
                    return obj

            return NewClass

        return class_rebuilder

    @class_decorator('first_method', 'second_method')
    class MySecondClass(object):
        """This class is decorated"""

        def first_method(self, *args, **kwargs):
            print "\t\tthis is a the MySecondClass.first_method"

        def second_method(self, *args, **kwargs):
            print "\t\tthis is the MySecondClass.second_method"

    print("=" * 50 + "     testcase_8     " + "=" * 50)
    test = MySecondClass()
    test.first_method()
    test.second_method()
    print("=" * 120)


def testcase_9():
    """一个示例性的字处理器，这种plugin的处理方式值得参考"""

    class WordProcessor(object):
        PLUGINS = []

        def process(self, text):
            for plugin in self.PLUGINS:
                text = plugin().cleanup(text)  # 注意这里是plugin()
            return text

        @classmethod
        def plugin(cls, plugin):
            cls.PLUGINS.append(plugin)

    @WordProcessor.plugin
    class CleanMdashesExtension(object):
        def cleanup(self, text):
            return text.replace('11111', u'333333')

    print("=" * 50 + "     testcase_9     " + "=" * 50)
    word = "111115678"
    processor = WordProcessor()
    print(processor.process(word))
    print("=" * 120)


if __name__ == "__main__":
    testcase_1()
    testcase_2()
    testcase_3()
    testcase_4()
    testcase_5()
    testcase_6()
    testcase_7()
    testcase_8()
    testcase_9()
