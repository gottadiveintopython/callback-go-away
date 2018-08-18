# -*- coding: utf-8 -*-

import unittest
from inspect import getgeneratorstate, GEN_CLOSED, GEN_SUSPENDED

import common_setup
from callbackgoaway import callbackgoaway, EventBase, Never


class Increament(EventBase):

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def __call__(self, resume_gen):
        self.obj.counter += 1
        resume_gen()


Inc = Increament


class NeverTestCase(unittest.TestCase):

    def setUp(self):
        self.counter = 0

    def test_single(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield Never()
            self.counter += 1
            yield 'TEST'
            self.counter += 1

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        self.assertEqual(self.counter, 0)
        # Never()後
        self.assertEqual(next(gen), 'TEST')
        self.assertEqual(self.counter, 1)
        with self.assertRaises(StopIteration):
            next(gen)
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        self.assertEqual(self.counter, 2)

    def test_operator_and(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield Never() & Inc(self)  # A
            self.assertEqual(self.counter, 1)
            self.counter += 1
            yield 'TEST'
            self.counter += 1

        gen = func()
        # この時点で既にA行の"Inc(self)"は実行されている
        self.assertEqual(self.counter, 1)
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        # A行の後のGeneratorの進め方はこちらに任されている
        self.assertEqual(next(gen), 'TEST')
        self.assertEqual(self.counter, 2)
        with self.assertRaises(StopIteration):
            next(gen)
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        self.assertEqual(self.counter, 3)

    def test_operator_or(self):

        @callbackgoaway
        def func():
            self.assertEqual(self.counter, 0)
            yield Never() | Inc(self)  # yield Inc(self) と同じ
            self.assertEqual(self.counter, 1)
            yield Never() | Never()  # A # yield Never() と同じ
            self.counter += 1
            yield 'TEST'
            self.counter += 1

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        self.assertEqual(self.counter, 1)
        # A行の後のGeneratorの進め方はこちらに任されている
        self.assertEqual(next(gen), 'TEST')
        self.assertEqual(self.counter, 2)
        with self.assertRaises(StopIteration):
            next(gen)
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)
        self.assertEqual(self.counter, 3)

    def test_close(self):

        @callbackgoaway
        def func():
            try:
                self.counter += 1
                yield Never()
            except GeneratorExit:
                self.counter += 1

        self.assertEqual(self.counter, 0)
        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        self.assertEqual(self.counter, 1)
        gen.close()
        self.assertEqual(self.counter, 2)


if __name__ == '__main__':
    unittest.main()
