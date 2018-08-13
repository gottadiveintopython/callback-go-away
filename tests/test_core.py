# -*- coding: utf-8 -*-

import unittest

import common_setup
from callbackgoaway import callbackgoaway, EventBase, And, Or


class Increament(EventBase):

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def __call__(self, resume_gen):
        self.obj.counter += 1
        resume_gen()


class CoreTestCase(unittest.TestCase):

    def setUp(self):
        self.counter = 0

    def increament(self, resume_gen):
        self.counter += 1
        resume_gen()

    def test_callbackgoaway(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield self.increament
            self.assertEqual(self.counter, 1)
            yield Increament(self)
            self.assertEqual(self.counter, 2)

        func()
        self.assertEqual(self.counter, 2)

    def test_and(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield Increament(self) & Increament(self)
            self.assertEqual(self.counter, 2)
            yield Increament(self) & Increament(self) & Increament(self)
            self.assertEqual(self.counter, 5)
            yield And(Increament(self), Increament(self), Increament(self))
            self.assertEqual(self.counter, 8)
            yield And(self.increament, self.increament, self.increament)
            self.assertEqual(self.counter, 11)

        func()
        self.assertEqual(self.counter, 11)

    def test_or(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)

            # orなので片方のincreamentの処理が終わった時点でgeneratorが再開する。
            # よって 1 しか増加しない。
            yield Increament(self) | Increament(self)
            self.assertEqual(self.counter, 1)

            # 同上
            yield Increament(self) | Increament(self) | Increament(self)
            self.assertEqual(self.counter, 2)

            # 同上
            yield Or(Increament(self), Increament(self), Increament(self))
            self.assertEqual(self.counter, 3)

            # 同上
            yield Or(self.increament, self.increament, self.increament)
            self.assertEqual(self.counter, 4)

        func()

        # generatorから戻ってきた時には全てのincreamentが実行されている
        self.assertEqual(self.counter, 11)

    def test_mix(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)

            # 一番左のincreamentが処理された時点でgeneratorが再開するので +1
            yield Increament(self) | Increament(self) & Increament(self)
            self.assertEqual(self.counter, 1)

            # 右以外のincreamentが処理された時点でgeneratorが再開するので +2
            yield Increament(self) & Increament(self) | Increament(self)
            self.assertEqual(self.counter, 3)

        func()

        # generatorから戻ってきた時には全てのincreamentが実行されている
        self.assertEqual(self.counter, 6)


if __name__ == '__main__':
    unittest.main()
