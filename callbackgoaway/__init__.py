# -*- coding: utf-8 -*-

__all__ = (
    'callbackgoaway', 'EventBase', 'Immediate', 'And', 'Or',
    'Generator', 'GeneratorFunction',
)

from functools import wraps, partial

from . import setup_logging
logger = setup_logging.get_logger(__file__)
debug = logger.debug


def callbackgoaway(create_gen):
    @wraps(create_gen)
    def wrapper(*args, **kwargs):
        gen = create_gen(*args, **kwargs)

        def resume_gen(*args, **kwargs):
            try:
                next(gen)(resume_gen)
            except StopIteration:
                pass

        resume_gen()
    return wrapper


class EventBase:

    def __and__(self, event):
        return And(self, event)

    def __or__(self, event):
        return Or(self, event)

    def __call__(self, resume_gen):
        raise NotImplementedError()


class Immediate(EventBase):
    def __call__(self, resume_gen):
        resume_gen()


class And(EventBase):

    def __init__(self, *events):
        super().__init__()
        self.events = tuple(events)

    def __call__(self, resume_gen):
        self.num_left = len(self.events)
        self.resume_gen = resume_gen
        self.triggered_event_ids = set()
        for event in self.events:
            event(partial(self.on_child_event, id(event)))

    def on_child_event(self, event_id, *args, **kwargs):
        if event_id not in self.triggered_event_ids:
            self.triggered_event_ids.add(event_id)
            self.num_left -= 1
            if self.num_left == 0:
                self.resume_gen()
            else:
                assert self.num_left > 0
        else:
            if __debug__:
                debug('Event(with id {}) triggered more than once.'.format(event_id))


class Or(EventBase):

    def __init__(self, *events):
        super().__init__()
        self.events = tuple(events)

    def __call__(self, resume_gen):
        self.is_triggered = False
        self.resume_gen = resume_gen
        for event in self.events:
            # The partial() here looks meaningless. But this is needed in order
            # to avoid possibility that 'self' to be GC-ed.
            # このpartial()は無意味に見えますが、これをしないとselfがゴミ収集の対象
            # にされる可能性がある。
            event(partial(self.on_child_event))

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
