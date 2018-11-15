# -*- coding: utf-8 -*-

import common_setup
from callbackgoaway import callbackgoaway


def _test():
    import pyglet

    window = pyglet.window.Window()
    label = pyglet.text.Label('Hello',
                              font_size=60,
                              x=window.width // 2, y=window.height // 2,
                              anchor_x='center', anchor_y='center', )

    @window.event
    def on_draw():
        window.clear()
        label.draw()

    @callbackgoaway
    def animate_label(label):
        from callbackgoaway.pyglet import Sleep as S

        yield S(1.5)
        while True:
            label.text = 'Do'
            label.color = (255, 255, 255, 255, )
            yield S(.5)
            label.text = 'You'
            yield S(.5)
            label.text = 'Like'
            yield S(.5)
            label.text = 'Pyglet?'
            yield S(2)
            label.text = 'Answer me!'
            label.color = (255, 0, 0, 255, )
            yield S(3)

    gen = animate_label(label)

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        gen.close()
        label.font_size = 20
        label.text = 'The animation was cancelled.'

    pyglet.app.run()


if __name__ == "__main__":
    _test()
