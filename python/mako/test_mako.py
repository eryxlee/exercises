# -*- coding: utf-8 -*-
'''
本文件是mako_template的单元测试文件。

模板语义上的检查需要检测生成的对应HTML内容是否正确。这里需要注意一些特殊字符
（如< > ' "等）在HTML的表示。

为了防止检查的地方模糊不清，最好将检查内容包含一部分临近的HTML。

'''
import os
import unittest

from mako.template import Template
from mako.lookup import TemplateLookup

from pyramid import testing
from pyramid.renderers import RendererHelper

_skip_test = True
_template_directory = os.path.dirname(__file__)
_data_directory = os.path.join(os.path.dirname(os.path.dirname(_template_directory)), 'data')
if not os.path.isdir(_data_directory):
    _data_directory = None


class TestMakoInPyramid(unittest.TestCase):
    """本实例演示在pyramid项目中，不通过view直接渲染template。

    在真实项目中，需要将mako.directories设置为project:templates，
    这里因没有Pyramid项目环境而使用了绝对路径。
    """
    def setUp(self):
        self.config = testing.setUp()

        from pyramid.interfaces import IRendererFactory
        from pyramid.mako_templating import renderer_factory

        self.request = testing.DummyRequest()
        self.context = testing.DummyResource()
        self.request.registry.settings = \
            {"mako.directories" : os.path.dirname(__file__)}
        self.request.registry.registerUtility(renderer_factory,
                                              IRendererFactory, name='.html')
        self.pyramid_system_value = {
            "request" : self.request,
            "req" : self.request,
            "context" : self.context,
        }

    def tearDown(self):
        testing.tearDown()

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_basic(self):
        value = {'returned_val' : 'a test val from the result of view'}
        self.request.request_val = 'a test val from request.'
        self.request.session['session_val'] = 'a test val from session.'

        # 这里的value参数就对应于pyramid view的返回值
        helper = RendererHelper(name="pyramid.html",
                                registry=self.request.registry)
        html = helper.render(value, self.pyramid_system_value)

        # 检查结果
        self.assertTrue(u'a test val from the result of view' in html)
        self.assertTrue(u'a test val from request' in html)
        self.assertTrue(os.path.dirname(__file__) in html)
        self.assertTrue(u'a test val from session' in html)


class TestMako(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_basic(self):
        value = {'rendered_val' : 'a test val to render'}

        html = Template(filename='basic.html',
                        input_encoding="utf-8").render(**value)

        # 检查第1段结果
        self.assertTrue("3 + 5 is: 8" in html)
        self.assertTrue("None value=None<br>" in html)
        self.assertTrue("empty string=<br>" in html)
        self.assertTrue("test string=test<br>" in html)
        self.assertTrue("None value after or=no<br>" in html)
        self.assertTrue("empty string after or=no<br>" in html)
        self.assertTrue("test string after or=test<br>" in html)

        # 检查第2段结果
        self.assertTrue("This is a comment which will not be rendered" not in html)
        self.assertTrue("This will be rendered ## and so will this." in html)

        # 检查第3段结果
        self.assertTrue("This is some Mako syntax which will not be executed: ${variable}" in html)

        # 检查第4段结果
        self.assertTrue("Welcome guest" in html)

        # 检查第5段结果，可以用\n代表html中的换行。注意别漏了空格。
        self.assertTrue("<ul>\n    <li>    <a href=\"http://jimmyg.org\">James</a>    </li>" in html)

        # 检查第6段结果
        self.assertTrue("An optional message: You must program in Python!" in html)

        # 检查第7段结果
        import datetime
        day = str(datetime.datetime.today())[0:10]
        self.assertTrue(day in html)

        self.assertTrue('a test val to render' in html)

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_hanzi(self):
        value = {'rendered_val' : u'a test val to render',
                 'rendered_hanzi' : u'中文'}

        # render 返回的是string，render_unicode返回unicode
        html = Template(filename='hanzi.html',
                        input_encoding="utf-8").render_unicode(**value)

        # 检查第1段结果
        self.assertTrue(u"模板里面的中文" in html)
        # 检查第2段结果
        self.assertTrue(u'a test val to render' in html)
        self.assertTrue(u'中文' in html)

        # 指定了output_encoding，再解码成unicode
        html = Template(filename='hanzi.html',
                        input_encoding="utf-8",
                        output_encoding='utf-8',
                        encoding_errors='replace').render(**value)
        html = html.decode('utf-8')

        # 检查第1段结果
        self.assertTrue(u"模板里面的中文" in html)
        # 检查第2段结果
        self.assertTrue(u'a test val to render' in html)
        self.assertTrue(u'中文' in html)

    @unittest.skipIf(_skip_test, "skipped while coding elsewhere")
    def test_filter(self):
        value = {'curl':'http://www.163.com/test<test> '}

        html = Template(filename='filter.html',
                        input_encoding="utf-8").render(**value)

        # 检查结果
#        self.assertTrue(u"1. The value is:  http://www.163.com/test&lt;test&gt; <br>" in html)
        # ${curl|u,n}
        # 这种使用方式相应的python代码是 filters.url_escape(curl)
        self.assertTrue(u"2. The value is:  http%3A%2F%2Fwww.163.com%2Ftest%3Ctest%3E+<br>" in html)
        # ${curl|h,n}
        # 这种使用方式相应的python代码是 filters.html_escape(curl)
        self.assertTrue(u"3. The value is:  http://www.163.com/test&lt;test&gt; <br>" in html)
        # ${curl|x,n}
        # 这种使用方式相应的python代码是 filters.xml_escape(curl)
        self.assertTrue(u"4. The value is:  http://www.163.com/test&lt;test&gt; <br>" in html)
        # ${curl|trim,n}
        # 这种使用方式相应的python代码是 filters.trim(curl)
        self.assertTrue(u"5. The value is:  http://www.163.com/test<test><br>" in html)
        # ${curl|entity,n}
        # 这种使用方式相应的python代码是 filters.html_entities_escape(curl)
        self.assertTrue(u"6. The value is:  http://www.163.com/test&lt;test&gt; <br>" in html)
        # ${curl|n}
        # 这种使用方式相应的python代码是 curl
        self.assertTrue(u"7. The value is:  http://www.163.com/test<test> <br>" in html)

    @unittest.skipIf(not _skip_test, "skipped while coding elsewhere")
    def test_defs(self):
        # 因在模板文件中使用了include等机制，只能使用lookup方法取得模板
        # 加参数 module_directory='/tmp/mako_modules' 可以在知道目录生成模板对应py文件
        mylookup = TemplateLookup(directories=[os.path.dirname(__file__)],
                                  module_directory=_data_directory,
                                  input_encoding="utf-8")
        html = mylookup.get_template('defs_main.html').render()

        # 检查结果
        self.assertTrue('result of add(1,2) is\n3\n<br>' in html)
        self.assertTrue('result of add2(1,2) is3<br>' in html)
        self.assertTrue('<a href="http://jimmyg.org">James</a>' in html)
        self.assertTrue('a text from other template' in html)

    @unittest.skipIf(not _skip_test, "skipped while coding elsewhere")
    def test_chain(self):
        value = {'greeting':'hello',
                 'name': 'yourname'}

        mylookup = TemplateLookup(directories=[os.path.dirname(__file__)],
                                  input_encoding="utf-8")
        html = mylookup.get_template('3levelchain_3.html').render(**value)

        # 检查结果
        self.assertTrue('User Administration &gt; Greetings' in html)
