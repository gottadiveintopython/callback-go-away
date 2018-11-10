# -*- coding: utf-8 -*-

__all__ = ('Sleep', 'Event', )

from functools import partial

from kivy.clock import Clock
schedule_once = Clock.schedule_once

from . import EventBase


class Sleep(EventBase):
    '''kivy,clock.Clock.schedule_once()用のWrapper'''

    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds

    def __call__(self, resume_gen):
        # The partial() here looks meaningless. But this is needed in order
        # to avoid weak reference
        # このpartial()は無意味に見えますが、これをしないとresume_genの弱参照が作ら
        # れる可能性があり、それによってresume_genが呼ばれない事がある。
        # (例えばresume_genが一時オブジェクトのinstance methodの時)
        schedule_once(partial(resume_gen), self.seconds)


class Event(EventBase):
    '''kivy.event.EventDispatcher用のWrapper'''

    def __init__(self, ed, name):
        super().__init__()
        self.bind_id = None
        self.ed = ed
        self.name = name

    def __call__(self, resume_gen):
        assert self.bind_id is None  # You can't re-use this instance
        self.bind_id = bind_id = self.ed.fbind(self.name, self.callback)
        assert bind_id > 0  # check if binding succeeded
        self.resume_gen = resume_gen

    def callback(self, ed, *args, **kwargs):
        ed.unbind_uid(self.name, self.bind_id)
        self.resume_gen()
