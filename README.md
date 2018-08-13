# Callback Go Away: Reducing annoying callback functions

Ugly code like this:

```python
from kivy.clock import Clock

def animate(label):
    s = Clock.schedule_once

    label.text = 'Do'

    def phase1(dt):
        label.text = 'You'
        s(phase2, .6)

    def phase2(dt):
        label.text = 'Like'
        s(phase3, .7)

    def phase3(dt):
        label.text = 'Kivy?'

    s(phase1, .5)
```

will become like this:

```python
from callbackgoaway import callbackgoaway
from callbackgoaway.kivy import Sleep as S

@callbackgoaway
def animate(label):
    label.text = 'Do'
    yield S(.5)
    label.text = 'You'
    yield S(.6)
    label.text = 'Like'
    yield S(.7)
    label.text = 'Kivy?'
```

and ugly code like this:

```python
from kivy.animation import Animation as A

def animate(image, image2):

    def on_complete(a, widget):
        a = A(width=300)
        a.bind(on_complete=on_complete2)
        a.start(image2)

    def on_complete2(a, widget):
        print('Done!')

    a = A(width=800)
    a.bind(on_complete=on_complete)
    a.start(image)
```

will become like this:

```python
from kivy.animation import Animation as A
from callbackgoaway import callbackgoaway
from callbackgoaway.kivy import Event as E

@callbackgoaway
def animate(image, image2):
    a = A(width=800)
    a.start(image1)
    yield E(a, 'on_complete')
    a = A(width=300)
    a.start(image2)
    yield E(a, 'on_complete')
    print('Done!')
```

Of course, you can use `Event` on any kind of `EventDispatcher`

```python
from kivy.core.audio import SoundLoader
from kivy.factory import Factory

from callbackgoaway import callbackgoaway
from callbackgoaway.kivy import Event as E

sound = SoundLoader(...)
button = Factory.Button(...)

@callbackgoaway
def func():
    sound.play()
    yield E(sound, 'on_stop')  # wait until the sound stops
    yield E(button, 'on_press')  # wait until the button is pressed
    yield E(button, 'text')  # wait until the text of the button is changed
```

## or-operator and and-operator

```python
from callbackgoaway import callbackgoaway, Or, And
from callbackgoaway.kivy import Event as E, Sleep as S

@callbackgoaway
def func():

    # wait until both events are triggered
    yield E(...) & E(...)

    # You can mix Event and Sleep
    yield E(...) & S(...)

    # wait until all four events are triggered
    yield And(E(...), S(...), E(...), E(...))

    # wait until either of events are triggered
    yield E(...) | E(...)
    # same
    yield E(...) | S(...)
    # same
    yield Or(E(...), S(...), E(...), E(...))
```
