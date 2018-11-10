# -*- coding: utf-8 -*-

import common_setup


def _test():
    from tkinter import Tk, Label
    from callbackgoaway import callbackgoaway

    root = Tk()
    label = Label(root, text='Hello', font=('', 80))
    label.pack()

    @callbackgoaway
    def animate_label(label):
        from callbackgoaway.tkinter import Sleep as S

        yield S(label, 1500)
        while True:
            label['text'] = 'Do'
            yield S(label, 500)
            label['text'] = 'You'
            yield S(label, 500)
            label['text'] = 'Like'
            yield S(label, 500)
            label['text'] = 'Tkinter?'
            yield S(label, 2000)
            label['text'] = 'Answer me!'
            yield S(label, 3000)

    gen = animate_label(label)

    def on_cliked(event):
        gen.close()
        label['text'] = 'The animation\nwas cancelled.'
    label.bind('<Button-1>', on_cliked)
    root.mainloop()


if __name__ == "__main__":
    _test()
