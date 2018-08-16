# Callback Go Away: Reducing annoying callback functions

このmoduleを用いる事で、しばしばKivyプログラミングで起こりうる、callback関数だらけの醜いcodeを減らす事ができます。例えば以下のようなLabelのtextを切り替えていくアニメーションのcodeは

```python
# Before
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

以下の様に書き換えられます。

```python
# After
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

この例のような **特にUserの操作に反応するわけではなくただひたすら逐一処理を行いたい時** 、言い換えるなら **CUIアプリのような書き方をしたい時** にこのmoduleは真価を発揮します。(Userの操作に関してもですがCUIアプリのように特定の時点でのみ入力を受け付けたいなら、このmoduleとの親和性は高いです)。

## このmoduleはいづれ要らなくなる?

ただ先に言っておきたいのが、Kivyがasyncioに対応した時(例えば[これ](https://github.com/kivy/kivy/pull/5241)が採用された時)にはこのmoduleなど使わずとも同じ事ができるようになるかもしれない事です。漠然とした予想なので絶対にとは言えないですが、対応した時には例えば以下のような書き方が可能になるはずです。

```python
# Future? Probabely like this
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
from callbackgoaway.kivy import Event as E


@callbackgoaway
def func():
    sound = SoundLoader(...)
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

## or演算子とand演算子

or演算子とand演算子を使うこともできます。

```python
from kivy.core.audio import SoundLoader
from kivy.factory import Factory
from kivy.animtion import Animation

from callbackgoaway import callbackgoaway, Or, And
from callbackgoaway.kivy import Event as E, Sleep as S

@callbackgoaway
def func():
    sound = SoundLoader(...)
    button = Factory.Button(...)
    anim = Animation(...)

    # wait until either the sound stops OR 5 seconds passes
    # 音が鳴り止む 'か' 5秒経つまで待機
    sound.play()
    yield E(sound, 'on_stop') | S(5)

    # wait until both the animation is completed AND the button is pressed
    # アニメーションが完了して 'かつ' buttonが押されるまで待機
    anim.start(button)
    yield E(anim, 'on_complete') & E(button, 'on_press')

    # if there are a lof of events, better to not use operators
    # たくさんEventがあるなら演算子を使わない方がいいかもしれません
    yield And(E(...), S(...), E(...), E(...))
    yield Or(E(...), S(...), S(...), E(...))
```

## 別のGeneratorを待機

```python
from callbackgoaway import (
    callbackgoaway, Generator as G, GeneratorFunction as GF,
)
from callbackgoaway.kivy import Event as E, Sleep as S

@callbackgoaway
def func():
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

    # wait until either the generator close or 3 seconds pass
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

## NeverとImmediate

`Never`と`Immediate`はかなり特殊なEventです。例えば以下のように書くと

```python
from callbackgoaway import callbackgoaway, Never

@callbackgoaway
def func():
    # wait eternally
    # 絶対に起こらないEvent
    yield Never()
```

Generatorはこのyieldの位置でずっと停まる事になります。じゃあどうするかというと外部から動かしてもらう事を期待します。

- `next(gen)` (再開)
- `gen.close()` (終了)

とは言うものの、現状では`@callbackgoaway`は内部で作った`Generator`へアクセスする方法を提供していないので実質そのような事はできません。いづれ作る予定なのでその時までお待ちください。  

`Immediate`は即座に起こるEventです。なので`yield E(button, 'on_press') & Immediate()` は `yield E(button, 'on_press')` と同じです。これを用いる事で以下のような`if文`を使った以下のようなcodeを

```python
@callbackgoaway
def func():
    if sound.state == 'play':
        yield E(button, 'on_press') & E(sound, 'on_stop')
    else:
        yield E(button, 'on_press')
```

以下のような`if式`を使ったcodeに書き換えれます。

```python
@callbackgoaway
def func():
    yield E(button, 'on_press') & (E(sound, 'on_stop') if sound.state == 'play' else Immediate())
```

...多分どこかで役に立つと思います。

## Examples

[Youtube](https://www.youtube.com/playlist?list=PLNdhqAjzeEGgS6FLxdXCdb_ldCwUCZLXu)
