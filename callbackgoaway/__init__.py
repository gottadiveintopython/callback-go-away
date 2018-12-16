# -*- coding: utf-8 -*-

__all__ = (
    'callbackgoaway', 'EventBase', 'Never', 'Immediate', 'Wait', 'And', 'Or',
    'Generator', 'GeneratorFunction',
)

from functools import wraps, partial
from collections import namedtuple

CallbackParameter = namedtuple('CallbackParameter', ('args', 'kwargs', ))


def callbackgoaway(create_gen):
    @wraps(create_gen)
    def wrapper(*args, **kwargs):
        gen = create_gen(*args, **kwargs)

        def resume_gen(*args, **kwargs):
            try:
                gen.send(CallbackParameter(args, kwargs, ))(resume_gen)
            except StopIteration:
                pass

        try:
            next(gen)(resume_gen)
        except StopIteration:
            pass

        return gen
    return wrapper


class EventBase:

    def __and__(self, event):
        return And(self, event)

    def __or__(self, event):
        return Or(self, event)

    def __call__(self, resume_gen):
        raise NotImplementedError()


class Never(EventBase):
    def __call__(self, resume_gen):
        pass


class Immediate(EventBase):
    def __call__(self, resume_gen):
        resume_gen()


class Wait(EventBase):

    def __init__(self, *, events, n=None):
        super().__init__()
        self.events = tuple(events)
        num_events = len(self.events)
        self.num_left = n if n is not None else num_events
        self.callbackparameter_list = [None, ] * num_events

    def __call__(self, resume_gen):
        self.resume_gen = resume_gen
        for event_id, event in enumerate(self.events):
            event(partial(self.on_child_event, event_id))

    def on_child_event(self, event_id, *args, **kwargs):
        cp_list = self.callbackparameter_list
        if cp_list[event_id] is None:
            cp_list[event_id] = CallbackParameter(args, kwargs)
            self.num_left -= 1
            if self.num_left == 0:
                self.resume_gen(*cp_list)


class And(Wait):

    def __init__(self, *events):
        super().__init__(events=events)


class Or(Wait):
    def __init__(self, *events):
        super().__init__(events=events, n=1)


class Generator(EventBase):

    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def __call__(self, resume_gen):
        gen = self.gen

        def internal_resume_gen(*args, **kwargs):
            try:
                next(gen)(internal_resume_gen)
            except StopIteration:
                resume_gen()
        internal_resume_gen()


class GeneratorFunction(Generator):

    def __init__(self, create_gen, *args, **kwargs):
        super().__init__(create_gen(*args, **kwargs))
