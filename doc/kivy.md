
このmoduleを用いる事で、GUIプログラミングでしばしば起こりうるcallback関数だらけの醜いcodeを減らす事ができます。例えば以下のようなLabelのtextを切り替えていくアニメーションのcodeは

```python
# Before
def animate_label(label):
    from kivy.clock import Clock
    s = Clock.schedule_once

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
        label.text = 'Kivy?'
        s(phase1, 2)

    s(phase1, 1.5)
```

以下の様に書き換えられます。

```python
# After
from callbackgoaway import callbackgoaway

@callbackgoaway
def animate_label(label):
    from callbackgoaway.kivy import Sleep as S

    yield S(1.5)
    while True:
        label.text = 'Do'
        yield S(.5)
        label.text = 'You'
        yield S(.5)
        label.text = 'Like'
        yield S(.5)
        label.text = 'Kivy?'
        yield S(2)
```

この例のような **特にUserの操作に反応するわけではなくただひたすら逐一処理を行いたい時** 、言い換えるなら **CUIアプリのような書き方をしたい時** にこのmoduleは真価を発揮します。(Userの操作に関してもですがCUIアプリのように特定の時点でのみ入力を受け付けたいなら、このmoduleとの親和性は高いです)。

## このmoduleはいづれ要らなくなる?

先に言っておきたいのが、Kivyがasyncioに対応した時(例えば[これ](https://github.com/kivy/kivy/pull/5241)が採用された時)にはこのmoduleなど使わずとも同じ事ができるようになるかもしれない事です。絶対にとは言えないですが、対応した時には例えば以下のような書き方が可能になるはずです。

```python
from asyncio import sleep

async def animate_label(label):
    await sleep(1.5)
    while True:
      label.text = 'Do'
      await sleep(.5)
      label.text = 'You'
      await sleep(.5)
      label.text = 'Like'
      await sleep(.5)
      label.text = 'Kivy?'
      await sleep(2)
```

なのでこのmoduleはあくまでそれまでの繋ぎとして考えてもらえたらと思います。

## Eventの待機

上の例ではSleepによる時間待機しかしてませんが、Eventの待機もできます。Eventというのは勿論`EventDispatcher`のEventの事です。kivyにおいては多くの物(`App`,`Widget`,`Sound`,`Animation`)が`EventDispatcher`の派生Classである為、それらを利用したcodeが容易に書けます。

```python
from kivy.core.audio import SoundLoader
from kivy.factory import Factory
from kivy.animtion import Animation

from callbackgoaway import callbackgoaway


@callbackgoaway
def func():
    from callbackgoaway.kivy import Event as E

    sound = SoundLoader.load(...)
    button = Factory.Button(...)
    anim = Animation(...)

    # wait until the sound stops
    # 音が鳴り止むまで待機
    sound.play()
    yield E(sound, 'on_stop')

    # wait until the button is pressed
    # buttonが押されるまで待機
    yield E(button, 'on_press')

    # wait until the text property of the button is changed
    # buttonのtextプロパティが変化するまで待機
    yield E(button, 'text')

    # wait for the completion of the animation
    # animationが完了するまで待機
    anim.start(button)
    yield E(anim, 'on_complete')
```

## 他の機能

他の機能に関してはどのGUIライブラリでも使い方が同じなので[別にまとめました](common.md)。
