# -*- coding: utf-8 -*-

import common_setup
from callbackgoaway import callbackgoaway


def _test():
    from textwrap import dedent
    from kivy.app import runTouchApp
    from kivy.lang import Builder

    root = Builder.load_string(dedent('''
        BoxLayout:
            orientation: 'vertical'
            padding: '10dp'
            Label:
                id: label
                font_size: '30sp'
            BoxLayout:
                spacing: '10dp'
                Button:
                    id: button_a
                    text: 'A'
                    font_size: '100sp'
                Button:
                    id: button_b
                    text: 'B'
                    font_size: '100sp'
                Button:
                    id: button_c
                    text: 'C'
                    font_size: '100sp'
        '''))

    @callbackgoaway
    def report_on_press():
        from callbackgoaway import Or
        from callbackgoaway.kivy import Event as E, Sleep as S

        label = root.ids.label
        button_a = root.ids.button_a
        button_b = root.ids.button_b
        button_c = root.ids.button_c

        yield S(0)
        while True:
            label.text = 'Press either of buttons.'
            params, __ = yield Or(E(button_a, 'on_press'),
                                  E(button_b, 'on_press'),
                                  E(button_c, 'on_press'), )
            if params[0] is not None:
                assert params[0].args[0] == button_a
                label.text = "A-Button was pressed"
            elif params[1] is not None:
                assert params[1].args[0] == button_b
                label.text = "B-Button was pressed"
            else:
                assert params[2].args[0] == button_c
                label.text = "C-Button was pressed"
            yield E(root, 'on_touch_down')
            yield S(0)

    report_on_press()
    runTouchApp(root)


if __name__ == "__main__":
    _test()
