# -*- coding: utf-8 -*-

import common_setup
from callbackgoaway import callbackgoaway


def _test():
    from kivy.app import runTouchApp
    from kivy.factory import Factory

    root = Factory.Label(font_size='30sp')

    @callbackgoaway
    def report_touch(label):
        from callbackgoaway.kivy import Event as E, Sleep as S

        yield S(0)
        while True:
            label.text = 'Touch anywhere'
            label.color = (1, 1, 1, 1, )
            param = yield E(label, 'on_touch_down')
            touch = param.args[1]
            label.text = f'You touched at pos {touch.pos}.'
            label.color = (1, 1, .3, 1, )
            yield E(label, 'on_touch_down')

    report_touch(root)
    runTouchApp(root)


if __name__ == "__main__":
    _test()
