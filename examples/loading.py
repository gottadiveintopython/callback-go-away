# -*- coding: utf-8 -*-

# from kivy.config import Config
# Config.set('graphics', 'width', 1280)
# Config.set('graphics', 'height', 720)
# Config.set('graphics', 'fullscreen', 1)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty

import common_setup


class Loading(BoxLayout):

    text = StringProperty('LOADING')
    font_size = NumericProperty('15sp')
    _gen = None  # instance属性の初期値としてのみ使っているclass属性

    def reset(self):
        '''widgetの状態をreset'''

        self.stop_anim()
        self.clear_widgets()

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
    def anim_main(self):
        from kivy.animation import Animation as A
        from callbackgoaway import Generator as G, And
        from callbackgoaway.kivy import Sleep as S, Event as E

        yield S(0)

        def anim_repeat_falldown(label, *, delay):
            yield S(delay)
            a = (
                A(pos_hint={'y': -0.1, }, t='out_cubic') +
                A(pos_hint={'y': 0, }, d=2, t='out_cubic') +
                A(pos_hint={'y': -1, }, top=self.y, t='out_cubic')
            )
            try:
                while True:
                    label.pos_hint['y'] = 1
                    a.start(label)
                    yield E(a, 'on_complete')
                    yield S(1)
            finally:
                a.cancel(label)

        labels = [Label(font_size=self.font_size,
                        text=c,
                        pos_hint={'y': 1, })
                  for c in self.text]
        add_widget = self.add_widget
        for label in labels:
            add_widget(label)
        gens = [
            anim_repeat_falldown(label, delay=index * 0.2)
            for index, label in enumerate(labels)
        ]
        try:
            yield And(*(G(gen) for gen in gens))
        finally:
            for gen in gens:
                gen.close()


if __name__ == '__main__':
    from kivy.app import runTouchApp
    root = Loading(spacing='50sp', padding='20sp', font_size='100sp')
    root.bind(on_touch_down=lambda *args: root.stop_anim())
    root.anim_main()
    runTouchApp(root)
