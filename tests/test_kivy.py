# -*- coding: utf-8 -*-

import unittest
from inspect import getgeneratorstate, GEN_CLOSED, GEN_SUSPENDED
import textwrap
from time import time

from kivy.factory import Factory
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import runTouchApp, stopTouchApp
from kivy.animation import Animation
from kivy.core.window import Window


import common_setup
from callbackgoaway import callbackgoaway
from callbackgoaway.kivy import Event, Sleep


class KivySleepTestCase(unittest.TestCase):
    DELTA = .2

    def tearDown(self):
        for child in Window.children[:]:
            Window.remove_widget(child)

    def test_single_sleep(self):
        root = Factory.Label(
            text="Test 'single' Sleep",
            font_size='30sp',
        )

        @callbackgoaway
        def func():
            S = Sleep
            yield S(0)
            start_time = time()
            yield S(.5)
            self.assertAlmostEqual(time() - start_time, .5, delta=self.DELTA)
            yield S(.5)
            self.assertAlmostEqual(time() - start_time, 1, delta=self.DELTA)
            stopTouchApp()

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        runTouchApp(root)

    def test_or_sleep(self):
        root = Factory.Label(
            text="Test 'or' Sleep",
            font_size='30sp',
        )

        @callbackgoaway
        def func():
            S = Sleep
            yield S(0)
            start_time = time()
            yield S(.5) | S(1)
            self.assertAlmostEqual(time() - start_time, .5, delta=self.DELTA)
            yield S(2) | S(1)
            self.assertAlmostEqual(time() - start_time, 1.5, delta=self.DELTA)
            stopTouchApp()

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        runTouchApp(root)

    def test_and_sleep(self):
        root = Factory.Label(
            text="Test 'and' Sleep",
            font_size='30sp',
        )

        @callbackgoaway
        def func():
            S = Sleep
            yield S(0)
            start_time = time()
            yield S(.5) & S(1)
            self.assertAlmostEqual(time() - start_time, 1, delta=self.DELTA)
            yield S(.5) & S(1)
            self.assertAlmostEqual(time() - start_time, 2, delta=self.DELTA)
            stopTouchApp()

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        # Clock.schedule_once(func, 0)
        runTouchApp(root)


class KivyEventTestCase(unittest.TestCase):

    def tearDown(self):
        for child in Window.children[:]:
            Window.remove_widget(child)

    def test_single_event(self):
        root = Factory.Label(
            text="Test 'single' Event",
            font_size='30sp',
        )

        @callbackgoaway
        def func():
            anim = Animation(opacity=0)
            anim.start(root)
            yield Event(anim, 'on_complete')
            self.assertEqual(root.opacity, 0)
            stopTouchApp()

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        runTouchApp(root)
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)

    def test_property_event(self):
        root = Factory.Label(
            text="Test property Event",
            font_size='30sp',
        )

        @callbackgoaway
        def func():
            Clock.schedule_once(lambda __: setattr(root, 'font_size', 20), .5)
            yield Event(root, 'font_size')
            self.assertEqual(root.font_size, 20)
            stopTouchApp()

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        runTouchApp(root)
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)

    def test_or_event(self):

        root = Builder.load_string(textwrap.dedent('''
        BoxLayout:
            Image:
                id: image
                source: 'data/logo/kivy-icon-256.png'
            Label:
                id: label
                text: "Test 'or' Event"
                font_size: sp(30)
        '''))

        @callbackgoaway
        def func():
            image = root.ids.image
            label = root.ids.label
            anim1 = Animation(opacity=0)
            anim2 = Animation(opacity=0, d=2)
            anim1.start(image)
            anim2.start(label)
            yield Event(anim1, 'on_complete') | Event(anim2, 'on_complete')
            self.assertEqual(image.opacity, 0)
            self.assertAlmostEqual(label.opacity, 0.5, delta=0.1)
            stopTouchApp()

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        runTouchApp(root)
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)

    def test_and_event(self):

        root = Builder.load_string(textwrap.dedent('''
        BoxLayout:
            Image:
                id: image
                source: 'data/logo/kivy-icon-256.png'
            Label:
                id: label
                text: "Test 'and' Event"
                font_size: sp(30)
        '''))

        @callbackgoaway
        def func():
            image = root.ids.image
            label = root.ids.label
            anim1 = Animation(opacity=0)
            anim2 = Animation(opacity=0, d=.5)
            anim1.start(image)
            anim2.start(label)
            yield Event(anim1, 'on_complete') & Event(anim2, 'on_complete')
            self.assertEqual(image.opacity, 0)
            self.assertEqual(label.opacity, 0)
            stopTouchApp()

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        runTouchApp(root)
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)


class KivyComplexTestCase(unittest.TestCase):

    def tearDown(self):
        for child in Window.children[:]:
            Window.remove_widget(child)

    def test_complex1(self):

        root = Builder.load_string(textwrap.dedent('''
        BoxLayout:
            Image:
                id: image
                source: 'data/logo/kivy-icon-256.png'
            Label:
                id: label
                text: "Complex Test"
                font_size: sp(30)
        '''))

        @callbackgoaway
        def func():
            A = Animation
            E = Event
            S = Sleep
            image = root.ids.image
            label = root.ids.label
            a1 = A(opacity=0, d=2)
            a2 = A(opacity=0)
            yield S(0)
            a1.start(image)
            a2.start(label)
            yield E(a1, 'on_complete') | S(.5) | E(a2, 'on_complete')
            self.assertAlmostEqual(image.opacity, 0.75, delta=0.1)
            self.assertAlmostEqual(label.opacity, 0.5, delta=0.1)
            yield E(a1, 'on_complete') | E(a2, 'on_complete')
            self.assertAlmostEqual(image.opacity, 0.5, delta=0.1)
            self.assertEqual(label.opacity, 0)
            yield E(a1, 'on_complete') | E(a2, 'on_complete')
            self.assertEqual(label.opacity, 0)
            self.assertEqual(image.opacity, 0)
            stopTouchApp()

        gen = func()
        self.assertEqual(getgeneratorstate(gen), GEN_SUSPENDED)
        runTouchApp(root)
        self.assertEqual(getgeneratorstate(gen), GEN_CLOSED)


if __name__ == "__main__":
    unittest.main()
