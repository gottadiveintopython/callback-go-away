# -*- coding: utf-8 -*-

__all__ = ('Sleep', 'Event', )

from kivy.clock import Clock
schedule_once = Clock.schedule_once

from . import EventBase


class Sleep(EventBase):
    '''kivy,clock.Clock.schedule_once()用のWrapper'''

    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds

    def __call__(self, resume_gen):
        schedule_once(resume_gen, self.seconds)


class Event(EventBase):
    '''kivy,event,EventDispatcher用のWrapper'''

    def __init__(self, ed, name):
        super().__init__()
        self.bind_id = None
        self.ed = ed
        self.name = name

    def __call__(self, resume_gen):
        assert self.bind_id is None  # You can't re-use this instance
        self.bind_id = self.ed.fbind(self.name, self.callback)
        self.resume_gen = resume_gen

    def callback(self, ed, *args, **kwargs):
        ed.unbind_uid(self.name, self.bind_id)
        self.resume_gen()
