# Callback Go Away: Reducing annoying callback functions

このmoduleを用いる事で、GUIプログラミングでしばしば起こりうるcallback関数だらけの醜いcodeを減らす事ができます。例えば以下のようなLabelのtextを切り替えていくアニメーションのcodeは

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

kivy版のREADMEを参照してください。

## Wait

kivy版のREADMEを参照してください。

## 別のgeneratorを待機

kivy版のREADMEを参照してください。

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

kivy版のREADMEを参照してください。
