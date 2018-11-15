# -*- coding: utf-8 -*-

__all__ = ('Sleep', 'Event', )

from functools import partial

from pyglet import clock
schedule_once = clock.schedule_once

from . import EventBase


class Sleep(EventBase):
    '''pyglet.clock.Clock.schedule_once()用のWrapper'''

    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds

    def __call__(self, resume_gen):
        schedule_once(partial(resume_gen), self.seconds)


class Event(EventBase):
    '''pyglet.event.EventDispatcher用のWrapper'''

    def __init__(self, ed, name):
        super().__init__()
        self.ed = ed
        self.name = name

    def __call__(self, resume_gen):
        self.resume_gen = resume_gen
        self.ed.push_handlers(**{self.name: self.callback})

    def callback(self, *args, **kwargs):
        self.ed.remove_handler(self.name, self.callback)
        self.resume_gen(*args, **kwargs)
