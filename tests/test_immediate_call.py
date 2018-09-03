# -*- coding: utf-8 -*-

import unittest
from inspect import getgeneratorstate, GEN_CLOSED, GEN_SUSPENDED

import common_setup
from callbackgoaway import (
    callbackgoaway, EventBase, Immediate, And, Or, Generator, GeneratorFunction,
    Wait,
)


class Increament(EventBase):

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def __call__(self, resume_gen):
        self.obj.counter += 1
        resume_gen()


Inc = Increament


class ImmediateCallTestCase(unittest.TestCase):

    def setUp(self):
        self.counter = 0

    def increament(self, resume_gen):
        self.counter += 1
        resume_gen()

    inc = increament

    def test_callbackgoaway(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield self.inc
            self.assertEqual(self.counter, 1)
            yield Inc(self)
            self.assertEqual(self.counter, 2)

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        self.assertEqual(self.counter, 2)

    def test_Immediate(self):
        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield Immediate()
            self.counter += 1

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        self.assertEqual(self.counter, 1)

    def test_wait(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield Wait(events=(Inc(self), Inc(self), ))
            self.assertEqual(self.counter, 2)
            yield Wait(events=(Inc(self), Inc(self), ), n=1)
            self.assertEqual(self.counter, 3)

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        self.assertEqual(self.counter, 4)

    def test_wait2(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield Wait(events=(Inc(self), Inc(self), ), n=3)

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        self.assertEqual(self.counter, 2)

    def test_operator_and(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield Inc(self) & Inc(self)
            self.assertEqual(self.counter, 2)
            yield Inc(self) & Inc(self) & Inc(self)
            self.assertEqual(self.counter, 5)
            yield And(Inc(self), Inc(self), Inc(self))
            self.assertEqual(self.counter, 8)
            yield And(self.inc, self.inc, self.inc)
            self.assertEqual(self.counter, 11)

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        self.assertEqual(self.counter, 11)

    def test_operator_or(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)

            # orなので片方のincreamentの処理が終わった時点でgeneratorが再開する。
            # よって 1 しか増加しない。
            yield Inc(self) | Inc(self)
            self.assertEqual(self.counter, 1)

            # 同上
            yield Inc(self) | Inc(self) | Inc(self)
            self.assertEqual(self.counter, 2)

            # 同上
            yield Or(Inc(self), Inc(self), Inc(self))
            self.assertEqual(self.counter, 3)

            # 同上
            yield Or(self.inc, self.inc, self.inc)
            self.assertEqual(self.counter, 4)

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        # generatorから戻ってきた時には全てのincreamentが実行されている
        self.assertEqual(self.counter, 11)

    def test_both_of_opeartors(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)

            # 一番左のincreamentが処理された時点でgeneratorが再開するので +1
            yield Inc(self) | Inc(self) & Inc(self)
            self.assertEqual(self.counter, 1)

            # 右以外のincreamentが処理された時点でgeneratorが再開するので +2
            yield Inc(self) & Inc(self) | Inc(self)
            self.assertEqual(self.counter, 3)

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        # generatorから戻ってきた時には全てのincreamentが実行されている
        self.assertEqual(self.counter, 6)

    def test_Generator_and_GeneratorFunction(self):

        def create_gen(times):
            for __ in range(times):
                yield Inc(self)

        @callbackgoaway
        def func():
            G = Generator
            GF = GeneratorFunction
            self.assertEqual(self.counter, 0)

            yield GF(create_gen, 2)
            self.assertEqual(self.counter, 2)
            yield G(create_gen(1))
            self.assertEqual(self.counter, 3)
            yield GF(create_gen, 2) | GF(create_gen, 1)
            self.assertEqual(self.counter, 5)
            yield GF(create_gen, 2) & GF(create_gen, 1)
            self.assertEqual(self.counter, 8)

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        self.assertEqual(self.counter, 9)


if __name__ == '__main__':
    unittest.main()
