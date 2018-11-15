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

## unbindの不具合？

以下のように複数のcallback関数を`bind()`した場合

```python
from tkinter import *


root = Tk()
button = Button(root, text='Push Me', font=('', 40))
button.pack()

bind_id = button.bind('<Button-1>', lambda event: print('1st callback'), '+')
print(bind_id)
bind_id2 = button.bind('<Button-1>', lambda event: print('2nd callback'), '+')
print(bind_id2)

button.unbind('<Button-1>', bind_id)  # A
# button.unbind('<Button-1>', bind_id2)  # B

root.mainloop()
```

A行とB行のどちらか一つを有効にしただけで両方のcallback関数が呼ばれなくなってしまいます。これが仕様なのか不具合なのか分かりませんが、[stackoverflowの投稿](https://stackoverflow.com/questions/6433369/deleting-and-changing-a-tkinter-event-binding)を参考にこれを修正するpatchを含めました。必要に応じて当ててください。

```python
# patchの当て方
from callbackgoaway.tkinter import patch_unbind
patch_unbind()
```

## 他の機能

他の機能に関してはどのGUIライブラリでも使い方が同じなので[別にまとめました](common.md)。
