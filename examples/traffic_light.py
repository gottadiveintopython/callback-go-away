# -*- coding: utf-8 -*-

import common_setup

from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ListProperty, ReferenceListProperty, ObjectProperty,
)


Builder.load_string('''
<TrafficLight>:
    _light_offset_x: self.spacing + self._diameter
    _diameter_candidate_1: (self.width - self.spacing * 2 - self.padding_min_x * 2) / 3
    _diameter_candidate_2: self.height - self.padding_min_y * 2
    _diameter: min(self._diameter_candidate_1, self._diameter_candidate_2)
    _padding_x: (self.width - 2 * self.spacing - 3 * self._diameter) / 2
    _padding_y: (self.height - self._diameter) / 2

    canvas:
        PushMatrix:

        # background
        Translate:
            xy: self.pos
        Color:
            rgba: self.background_color
        RoundedRectangle:
            pos: 0, 0
            size: self.size
            radius: (self.height / 2, ) * 2

        # left light
        Translate:
            xy: self._padding
        Color:
            rgba: self._current_left_color
        Ellipse:
            pos: 0, 0
            size: self._diameter, self._diameter

        # center light
        Translate:
            x: self._light_offset_x
        Color:
            rgba: self._current_center_color
        Ellipse:
            pos: 0, 0
            size: self._diameter, self._diameter

        # right light
        Translate:
            x: self._light_offset_x
        Color:
            rgba: self._current_right_color
        Ellipse:
            pos: 0, 0
            size: self._diameter, self._diameter

        PopMatrix:
''')


class TrafficLight(Widget):
    left_color = ListProperty((0, .8, .8, 1, ))
    center_color = ListProperty((.8, .8, 0, 1, ))
    right_color = ListProperty((1, .2, .2, 1, ))
    background_color = ListProperty((.2, .2, .2, 1, ))
    light_off_color = ListProperty((.1, .1, .1, 1, ))
    spacing = NumericProperty(20)  # 信号機のライトの間隔
    padding_min_x = NumericProperty(20)
    padding_min_y = NumericProperty(20)
    padding_min = ReferenceListProperty(padding_min_x, padding_min_y)
    _padding_x = NumericProperty()
    _padding_y = NumericProperty()
    _padding = ReferenceListProperty(_padding_x, _padding_y)
    _light_offset_x = NumericProperty()
    _diameter = NumericProperty()  # 信号機のライトの直径
    _diameter_candidate_1 = NumericProperty()
    _diameter_candidate_2 = NumericProperty()
    _current_left_color = ListProperty()
    _current_center_color = ListProperty()
    _current_right_color = ListProperty()
    _gen = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reset()

    def reset(self):
        '''widgetの状態をreset'''

        self.stop_anim()
        light_off_color = self.light_off_color[:]
        self._current_left_color = light_off_color
        self._current_center_color = light_off_color
        self._current_right_color = light_off_color

    def stop_anim(self):
        '''animationが再生中であれば停める'''

        if self._gen is not None:
            self._gen.close()
            self._gen = None

    def animation(create_gen):
        '''gengeratorの後始末を自動で行う為のdecorator'''

        from functools import wraps
        from callbackgoaway import callbackgoaway

        @wraps(create_gen)
        def wrapper(self, *args, **kwargs):
            self.reset()
            self._gen = callbackgoaway(create_gen)(self, *args, **kwargs)
        return wrapper

    @animation
    def anim_normal(self):
        '''信号機の明かりが 右 -> 左 -> 中央 -> 右 -> ... の順に点灯する'''

        from callbackgoaway.kivy import Sleep as S, Event as E
        from kivy.animation import Animation as A

        yield S(0)
        light_off_color = self.light_off_color[:]
        a = None
        try:
            while True:
                a = A(_current_right_color=self.right_color[:], d=.3)
                a.start(self)
                yield E(a, 'on_complete')
                yield S(2)
                a = A(_current_right_color=light_off_color[:], d=.3)
                a.start(self)
                yield E(a, 'on_complete')
                a = A(_current_left_color=self.left_color[:], d=.3)
                a.start(self)
                yield E(a, 'on_complete')
                yield S(2)
                a = A(_current_left_color=light_off_color[:], d=.3)
                a.start(self)
                yield E(a, 'on_complete')
                a = A(_current_center_color=self.center_color[:], d=.3)
                a.start(self)
                yield E(a, 'on_complete')
                yield S(1)
                a = A(_current_center_color=light_off_color[:], d=.3)
                a.start(self)
                yield E(a, 'on_complete')
        finally:
            if a is not None:
                a.cancel(self)

    @animation
    def anim_blink_center_light(self):
        '''信号機の中央の明かりが点滅する'''

        from callbackgoaway.kivy import Sleep as S, Event as E
        from kivy.animation import Animation as A

        yield S(0)
        a = None
        try:
            while True:
                a = A(_current_center_color=self.center_color[:], d=.7)
                a.start(self)
                yield E(a, 'on_complete')
                yield S(.1)
                a = A(_current_center_color=self.light_off_color[:], d=.7)
                a.start(self)
                yield E(a, 'on_complete')
                yield S(.1)
        finally:
            if a is not None:
                a.cancel(self)

    @animation
    def anim_random(self):
        '''無作為に明かりを点灯させる'''

        from callbackgoaway import Generator as G, And
        from callbackgoaway.kivy import Sleep as S, Event as E
        from kivy.animation import Animation as A
        from kivy.utils import get_random_color
        from random import random

        yield S(0)
        light_off_color = self.light_off_color[:]

        def random_duration():
            return random() + .5

        def anim_one_light(property_name):
            yield S(0)
            a = None
            try:
                while True:
                    yield S(random_duration())
                    a = A(**{property_name: get_random_color(),
                             'duration': random_duration()})
                    a.start(self)
                    yield E(a, 'on_complete')
                    yield S(random_duration())
                    a = A(**{property_name: light_off_color[:],
                             'duration': random_duration()})
                    a.start(self)
                    yield E(a, 'on_complete')
            finally:
                if a is not None:
                    a.cancel(self)

        gens = [anim_one_light(f'_current_{name}_color')
                for name in ('left', 'right', 'center', )]
        try:
            yield And(*(G(gen) for gen in gens))
        finally:
            for gen in gens:
                gen.close()


def _test():
    import textwrap

    root = Builder.load_string(textwrap.dedent('''
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp', '20dp'
        spacing: '20dp'
        BoxLayout:
            Widget:
                size_hint_x: 3
            GridLayout:
                cols: 2
                spacing: '5dp'
                Label:
                    text: 'normal'
                CheckBox:
                    group: 'anim'
                    on_active: if args[1]: light.anim_normal()
                Label:
                    text: 'blink center'
                CheckBox:
                    group: 'anim'
                    on_active: if args[1]: light.anim_blink_center_light()
                Label:
                    text: 'random'
                CheckBox:
                    group: 'anim'
                    on_active: if args[1]: light.anim_random()
            Widget:
                size_hint_x: 3
        TrafficLight:
            id: light
    '''))
    runTouchApp(root)


if __name__ == "__main__":
    _test()
