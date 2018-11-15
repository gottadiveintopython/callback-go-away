# -*- coding: utf-8 -*-

__all__ = ('Sleep', 'Event', 'patch_unbind')


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


_old_unbind = None


def _new_unbind(self, sequence, funcid=None):
    """Unbind for this widget for event SEQUENCE  the
    function identified with FUNCID."""
    if not funcid:
        self.tk.call('bind', self._w, sequence, '')
        return
    func_callbacks = self.tk.call('bind', self._w, sequence, None).split('\n')
    new_callbacks = [l for l in func_callbacks if l[6:6 + len(funcid)] != funcid]
    self.tk.call('bind', self._w, sequence, '\n'.join(new_callbacks))
    self.deletecommand(funcid)


def patch_unbind():
    from tkinter import Misc

    global _old_unbind
    if _old_unbind is None:
        _old_unbind = Misc.unbind
        Misc.unbind = _new_unbind
