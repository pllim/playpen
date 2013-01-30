"""http://stackoverflow.com/questions/4858298/python-3-class-template-function-that-returns-a-parameterized-class"""

class Template(object):
    __myname__ = 'template'

    def run(self):
        return 'running'


def make_class(name):
    return type(name, (Template, ), {'__myname__': name})


def test():
    new_class = make_class('aaa')
    a = new_class()

    assert isinstance(a, Template)

    assert Template.__myname__ == 'template'
    assert new_class.__myname__ == 'aaa'
    assert a.__myname__ == new_class.__myname__

    assert a.run() == 'running'


if __name__ == '__main__':
    test()
