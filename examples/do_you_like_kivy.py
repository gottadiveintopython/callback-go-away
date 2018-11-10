# -*- coding: utf-8 -*-

import common_setup
from callbackgoaway import callbackgoaway


def _test():
    from kivy.app import runTouchApp
    from kivy.factory import Factory

    root = Factory.Label(
        text='Hello', font_size='100sp', markup=True,
        outline_color=(1, 1, 1, 1, ), outline_width=2,
    )

    @callbackgoaway
    def animate_label(label):
        from callbackgoaway.kivy import Sleep as S

        yield S(1.5)
        while True:
            label.text = 'Do'
            label.color = (0, 0, 0, 1, )
            yield S(.5)
            label.text = 'You'
            yield S(.5)
            label.text = 'Like'
            yield S(.5)
            label.text = 'Kivy?'
            yield S(2)
            label.text = 'Answer me!'
            label.color = (1, 0, 0, 1, )
            yield S(3)

    gen = animate_label(root)

    def on_touch_down(label, touch):
        gen.close()
        label.text = 'The animation\nwas cancelled.'
        label.color = (.5, 0, .5, 1, )
    root.bind(on_touch_down=on_touch_down)
    runTouchApp(root)


if __name__ == "__main__":
    _test()
