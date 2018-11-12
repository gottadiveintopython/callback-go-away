tkinter版は[こちら](README_tkinter.md)  
tkinter versioin is [here](README_tkinter.md)  

# Callback Go Away: Reducing annoying callback functions

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
def animate(label):
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

async def animate(label):
    label.text = 'Do'
    await sleep(.5)
    label.text = 'You'
    await sleep(.6)
    label.text = 'Like'
    await sleep(.7)
    label.text = 'Kivy?'
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

## `|`演算子と`&`演算子

`|`演算子と`&`演算子を使うことで2つ以上のEventを同時に待機できます。

```python
from kivy.core.audio import SoundLoader
from kivy.factory import Factory
from kivy.animtion import Animation

from callbackgoaway import callbackgoaway

@callbackgoaway
def func():
    from callbackgoaway import Or, And
    from callbackgoaway.kivy import Event as E, Sleep as S

    sound = SoundLoader.load(...)
    button = Factory.Button(...)
    anim = Animation(...)

    # wait until EITHER the sound stops OR 5 seconds passes
    # 音が鳴り止む か 5秒経つまで待機
    sound.play()
    yield E(sound, 'on_stop') | S(5)

    # wait until BOTH the animation is completed AND the button is pressed
    # アニメーションが完了して かつ buttonが押されるまで待機
    anim.start(button)
    yield E(anim, 'on_complete') & E(button, 'on_press')

    # if there are a lof of events, better to not use operators
    # たくさんEventがあるなら演算子を使わずに以下のようにした方が効率は良いです
    yield And(E(...), S(...), E(...), E(...))
    yield Or(E(...), S(...), S(...), E(...))
```

## Wait

Waitを用いる事で、与えられたEventのうち任意の数だけ待機できます

```python
from kivy.core.audio import SoundLoader
from kivy.factory import Factory
from kivy.animtion import Animation

from callbackgoaway import callbackgoaway

@callbackgoaway
def func():
    from callbackgoaway import Wait
    from callbackgoaway.kivy import Event as E, Sleep as S

    sound = SoundLoader.load(...)
    button = Factory.Button(...)

    # 音が鳴り止む, 5秒経つ, Buttonが押される,
    # の3つのEventの内のどれか2つが起きるまで待機
    sound.play()
    yield Wait(
        events=(E(sound, 'on_stop'), S(5), E(button, 'on_press'), ),
        n=2,
    )
```

## 別のgeneratorを待機

```python
from callbackgoaway import callbackgoaway

@callbackgoaway
def func():
    from callbackgoaway import Generator as G, GeneratorFunction as GF
    from callbackgoaway.kivy import Event as E, Sleep as S

    def another_gen1(duration):
        ...
        yield S(duration)
        ...
    def another_gen2():
        ...
        yield E(anim, 'on_complete')
        ...
    # nothing special
    # 普通のsub generator呼び出し
    yield from another_gen1(1)

    # wait until either the generator close or 3 seconds passes
    # Generatorが終わるか3秒経つまで待機
    yield G(another_gen1(1)) | S(3)

    # wait until either of two generators close
    # どちらかのGeneratorが終わるまで待機
    yield G(another_gen1(1)) | G(another_gen2())

    # wait until both of two generators close
    # 両方のGeneratorが終わるまで待機
    yield G(another_gen1(1)) & G(another_gen2())

    # equivalent to right above
    # 真上の式と等価な式
    yield GF(another_gen1, 1) & GF(another_gen2)
```

## generatorオブジェクトを操作

`@callbackgoaway`で修飾された関数はgeneratorオブジェクトを返すので、以下のような無限loopを書いてもそれを外部から止める手段がある事を意味します。

```python
from kivy.app import runTouchApp
from kivy.factory import Factory
from callbackgoaway import callbackgoaway

root = Factory.Label(
    text='Hello', font_size='100sp', markup=True,
    outline_color=(1, 1, 1, 1, ), outline_width=2,
)

@callbackgoaway
def animate_label(label):
    from callbackgoaway.kivy import Sleep as S

    yield S(1.5)
    while True:  # 無限loop!!
        label.text = 'Do'
        label.color = (0, 0, 0, 1, )
        yield S(.5)
        label.text = 'You'
        yield S(.5)
        label.text = 'Like'
        yield S(.5)
        label.text = 'Kivy?'
        yield S(2)
        label.text = 'Answer me!'
        label.color = (1, 0, 0, 1, )
        yield S(3)

gen = animate_label(root)  # generatorを取得

def on_touch_down(label, touch):
    gen.close()  # generatorを終了させる
    label.text = 'The animation\nwas cancelled.'
    label.color = (.5, 0, .5, 1, )
root.bind(on_touch_down=on_touch_down)
runTouchApp(root)
```

## NeverとImmediate

`Never`と`Immediate`は特殊なEventです。例えば以下のように書くと

```python
from callbackgoaway import callbackgoaway

@callbackgoaway
def func():
    from callbackgoaway import Never

    # wait eternally
    # 絶対に起こらないEvent
    yield Never()
```

generatorはこのyieldの位置でずっと停まる事になります。じゃあどうやって進めるかというと外部から動かしてあげます。

```python
from callbackgoaway import callbackgoaway


@callbackgoaway
def func():
    from callbackgoaway import Never

    print('func(): start')
    yield Never()
    print('func(): end')

gen = func()
print('returned from func()')
gen.close()
print('--------------')
gen = func()
print('returned from func()')
try:
    next(gen)
except StopIteration:
    pass
```

```text
func(): start
returned from func()
--------------
func(): start
returned from func()
func(): end
```

`Immediate`ですが、これは即座に起こるEventです。なので`yield E(button, 'on_press') & Immediate()` は `yield E(button, 'on_press')` と同じです。これを用いる事で以下のような`if文`を使った以下のようなcodeを

```python
from callbackgoaway import callbackgoaway

@callbackgoaway
def func():
    if sound.state == 'play':
        yield E(button, 'on_press') & E(sound, 'on_stop')
    else:
        yield E(button, 'on_press')
```

以下のような`if式`を使ったcodeに書き換えれます。

```python
from callbackgoaway import callbackgoaway, Immediate

@callbackgoaway
def func():
    yield E(button, 'on_press') & (E(sound, 'on_stop') if sound.state == 'play' else Immediate())
```

また`& Immediate()`と同じで`| Never()`も`if式`で使えるでしょう。



## Examples

[Youtube](https://www.youtube.com/playlist?list=PLNdhqAjzeEGgS6FLxdXCdb_ldCwUCZLXu)
