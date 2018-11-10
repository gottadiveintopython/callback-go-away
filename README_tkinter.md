# Callback Go Away: Reducing annoying callback functions

このmoduleを用いる事で、しばしばGUIプログラミングで起こりうるcallback関数だらけの醜いcodeを減らす事ができます。例えば以下のようなLabelのtextを切り替えていくアニメーションのcodeは

```python
# Before
def animate_label(label):

    def phase1():
        label['text'] = 'Do'
        label.after(500, phase2)

    def phase2():
        label['text'] = 'You'
        label.after(500, phase3)

    def phase3():
        label['text'] = 'Like'
        label.after(500, phase4)

    def phase4():
        label['text'] = 'Tkinter?'
        label.after(2000, phase1)

    label.after(1500, phase1)
```

以下の様に書き換えられます。

```python
# After
@callbackgoaway
def animate_label(label):
    from callbackgoaway.tkinter import Sleep as S

    yield S(label, 1500)
    while True:
        label['text'] = 'Do'
        yield S(label, 500)
        label['text'] = 'You'
        yield S(label, 500)
        label['text'] = 'Like'
        yield S(label, 500)
        label['text'] = 'Tkinter?'
        yield S(label, 2000)
```

この例のような **特にUserの操作に反応するわけではなくただひたすら逐一処理を行いたい時** 、言い換えるなら **CUIアプリのような書き方をしたい時** にこのmoduleは真価を発揮します。(Userの操作に関してもですがCUIアプリのように特定の時点でのみ入力を受け付けたいなら、このmoduleとの親和性は高いです)。

## Eventの待機

上の例ではSleepによる時間待機しかしてませんが、Eventの待機もできます。

```python
from callbackgoaway import callbackgoaway


@callbackgoaway
def func():
    from callbackgoaway.tkinter import Event as E

    label = Label(...)

    # wait until the label is pressed
    # labelがclickされるまで待機
    yield E(label, '<Button-1>')
```

## `|`演算子と`&`演算子

`|`演算子と`&`演算子を使うことで2つ以上のEventを同時に待機できます。

```python
from callbackgoaway import callbackgoaway


@callbackgoaway
def func():
    from callbackgoaway.tkinter import Sleep as S, Event as E

    label = Label(...)

    # wait until EITHER the label is pressed OR 2 seconds passes
    # labelがclickされる か 2秒経つまで待機
    yield E(label, '<Button-1>') | S(label, 2000)

    # wait until BOTH the label is pressed AND 2 seconds passes
    # labelがclickされ かつ 2秒経つまで待機
    yield E(label, '<Button-1>') & S(label, 2000)
```

## Wait

Waitを用いる事で、与えられたEventのうち任意の数だけ待機できます

```python
from callbackgoaway import callbackgoaway

@callbackgoaway
def func():
    from callbackgoaway import Wait
    from callbackgoaway.tkinter import Event as E, Sleep as S

    label = Label(...)

    # labelがclickされる, 5秒経つ, Keyboardが押される,
    # の3つのEventの内のどれか2つが起きるまで待機
    yield Wait(
        events=(E(label, '<Button-1>'), S(5000), E(label, '<Key>'), ),
        n=2,
    )
```

## 別のgeneratorを待機

```python
from callbackgoaway import callbackgoaway

@callbackgoaway
def func():
    from callbackgoaway import Generator as G, GeneratorFunction as GF
    from callbackgoaway.tkinter import Event as E, Sleep as S

    def another_gen1(duration):
        ...
        yield S(duration)
        ...
    def another_gen2():
        ...
        yield E(widget, '<Key>')
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
from tkinter import Tk, Label
from callbackgoaway import callbackgoaway

root = Tk()
label = Label(root, text='Hello', font=('', 80))
label.pack()

@callbackgoaway
def animate_label(label):
    from callbackgoaway.tkinter import Sleep as S

    yield S(label, 1500)
    while True:  # 無限loop!!
        label['text'] = 'Do'
        yield S(label, 500)
        label['text'] = 'You'
        yield S(label, 500)
        label['text'] = 'Like'
        yield S(label, 500)
        label['text'] = 'Tkinter?'
        yield S(label, 2000)
        label['text'] = 'Answer me!'
        yield S(label, 3000)

gen = animate_label(label)  # generatorを取得

def on_cliked(event):
    gen.close()  # generatorを終了させる
    label['text'] = 'The animation\nwas cancelled.'
label.bind('<Button-1>', on_cliked)
root.mainloop()
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
    if some_condition:
        yield E(label, '<Key>') & E(button, '<Button-1>')
    else:
        yield E(label, '<Key>')
```

以下のような`if式`を使ったcodeに書き換えれます。

```python
from callbackgoaway import callbackgoaway, Immediate

@callbackgoaway
def func():
    yield E(label, '<Key>') & (E(button, '<Button-1>') if some_condition  else Immediate())
```

また`& Immediate()`と同じで`| Never()`も`if式`で使えるでしょう。
