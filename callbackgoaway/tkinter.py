# -*- coding: utf-8 -*-

__all__ = ('Sleep', 'Event', )


from . import EventBase


class Sleep(EventBase):
    '''tkinterのwidgetのafter()用のWrapper'''

    def __init__(self, widget, milliseconds):
        super().__init__()
        self.widget = widget
        self.milliseconds = milliseconds

    def __call__(self, resume_gen):
        self.widget.after(self.milliseconds, resume_gen)


class Event(EventBase):
    '''tkinterのwidgetのbind()用のWrapper'''

    def __init__(self, widget, name):
        super().__init__()
        self.bind_id = None
        self.widget = widget
        self.name = name

    def __call__(self, resume_gen):
        assert self.bind_id is None  # You can't re-use this instance
        self.bind_id = self.widget.bind(self.name, self.callback, '+')
        self.resume_gen = resume_gen

    def callback(self, event):
        self.widget.unbind(self.name, self.bind_id)
        self.resume_gen()
