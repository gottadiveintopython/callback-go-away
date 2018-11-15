# -*- coding: utf-8 -*-

__all__ = (
    'callbackgoaway', 'EventBase', 'Never', 'Immediate', 'Wait', 'And', 'Or',
    'Generator', 'GeneratorFunction',
)

from functools import wraps, partial
from collections import namedtuple

from . import setup_logging
logger = setup_logging.get_logger(__file__)
debug = logger.debug


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
        self.initial_num_left = n if n is not None else len(self.events)

    def __call__(self, resume_gen):
        self.num_left = self.initial_num_left
        self.resume_gen = resume_gen
        self.triggered_event_ids = set()
        for event_id, event in enumerate(self.events):
            event(partial(self.on_child_event, event_id))

    def on_child_event(self, event_id, *args, **kwargs):
        if event_id not in self.triggered_event_ids:
            self.triggered_event_ids.add(event_id)
            self.num_left -= 1
            if self.num_left == 0:
                self.resume_gen()
        else:
            if __debug__:
                debug('Event(with id {}) triggered more than once.'.format(event_id))


class And(Wait):

    def __init__(self, *events):
        super().__init__(events=events)


class Or(EventBase):

    def __init__(self, *events):
        super().__init__()
        self.events = tuple(events)

    def __call__(self, resume_gen):
        self.is_triggered = False
        self.resume_gen = resume_gen
        for event in self.events:
            event(self.on_child_event)

    def on_child_event(self, *args, **kwargs):
        if not self.is_triggered:
            self.is_triggered = True
            self.resume_gen()


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
