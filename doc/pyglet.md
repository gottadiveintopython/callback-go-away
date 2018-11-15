
このmoduleを用いる事で、GUIプログラミングでしばしば起こりうるcallback関数だらけの醜いcodeを減らす事ができます。例えば以下のようなLabelのtextを切り替えていくアニメーションのcodeは

```python
# Before
def animate_label(label):
    from pyglet import clock
    s = clock.schedule_once

    def phase1(dt):
        label.text = 'Do'
        s(phase2, .5)

    def phase2(dt):
        label.text = 'You'
        s(phase3, .5)

    def phase3(dt):
        label.text = 'Like'
        s(phase4, .5)

    def phase4(dt):
        label.text = 'Pyglet?'
        s(phase1, 2)

    s(phase1, 1.5)
```

以下の様に書き換えられます。

```python
# After
from callbackgoaway import callbackgoaway

@callbackgoaway
def animate_label(label):
    from callbackgoaway.pyglet import Sleep as S

    yield S(1.5)
    while True:
        label.text = 'Do'
        yield S(.5)
        label.text = 'You'
        yield S(.5)
        label.text = 'Like'
        yield S(.5)
        label.text = 'Pyglet?'
        yield S(2)
```

この例のような **特にUserの操作に反応するわけではなくただひたすら逐一処理を行いたい時** 、言い換えるなら **CUIアプリのような書き方をしたい時** にこのmoduleは真価を発揮します。(Userの操作に関してもですがCUIアプリのように特定の時点でのみ入力を受け付けたいなら、このmoduleとの親和性は高いです)。

## Eventの待機

上の例ではSleepによる時間待機しかしてませんが、EventDispatcherのEventの待機もできます。

```python
import pyglet

window = pyglet.window.Window()

from callbackgoaway import callbackgoaway


@callbackgoaway
def func():
    from callbackgoaway.pyglet import Event as E

    # wait until the mouse button is pressed
    # mouseのbuttonが押されるまで待機
    yield E(window, 'on_mouse_press')
```

## 他の機能

他の機能に関してはどのGUIライブラリでも使い方が同じなので[別にまとめました](common.md)。
