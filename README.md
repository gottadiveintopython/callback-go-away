# Callback Go Away : Reducing annoying callback functions

このmoduleを用いる事で、GUIプログラミングでしばしば起こりうるcallback関数だらけの醜いcodeを減らす事ができます。例えばtkinter向けの以下のコードは

```python
def animate_label(label):
    label['text'] = 'Hello'

    def callback():
        label['text'] = 'World'

    label.after(1000, callback)  # callbackが1秒後(1000ミリ秒後)実行される
```

以下のように書き換えられます。

```python
from callbackgoaway import callbackgoaway
from callbackgoaway.tkinter import Sleep

@callbackgoaway
def animate_label(label):
    label['text'] = 'Hello'
    yield Sleep(label, 1000)
    label['text'] = 'World'
```

詳しくはお使いのGUIライブラリ毎のdocumentationを読んでください。

- [Tkinter](doc/tkinter.md)
- [Kivy](doc/kivy.md)

## Test環境(Test Environment)

- Python 3.6.3
- Linux Mint 18.2 (derived from Ubuntu 16.04LTS)
