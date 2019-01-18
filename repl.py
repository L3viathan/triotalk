import sys
from collections.abc import Callable, Hashable
import trio
from markdown import markdown

old_dh = sys.displayhook
old_eh = sys.excepthook

state = {"language": "english", "slide": 0}
mode = "normal"

bindings = {"l": ("language", ["german", "english", "romanian"])}

def load_slides():
    global slides
    with open(f"{state['language']}.md") as f:
        slides = f.read().split("\n====\n")
load_slides()


def show():
    nr = state["slide"]
    if nr >= len(slides):
        state["slide"] -= 1
    print(markdown(slides[state["slide"]]).rstrip())
    print(f"[{state['slide']+1}/{len(slides)}]".rjust(markdown.renderer.columns))


def ask(key, choices, phrase=None, char=None):
    global mode
    if phrase:
        print(phrase)
    for i, c in enumerate(choices):
        print(f"[{i}] {c}")

    def answer(response):
        global mode
        choice = choices[int(response)]
        print(f"Switching {key} to {choice}")
        state[key] = choice
        mode = "normal"
        if char == "l":
            load_slides()
            show()

    mode = answer


def ask_slidenr(total):
    global mode

    def answer(response):
        global mode
        if isinstance(response, int):
            state["slide"] = response - 1
        elif isinstance(response, str) and response[1:].isdigit():
            if response[0] == "+":
                state["slide"] += int(response[1:])
            if response[0] == "-":
                state["slide"] -= int(response[1:])
        mode = "normal"
        show()

    print(f"slide? [1–{total}]")
    mode = answer


def dh(something):
    if not isinstance(something, Hashable):
        return old_dh(something)
    elif isinstance(mode, Callable):
        return mode(something)
    elif something in bindings:
        return ask(*bindings[something], char=something)
    elif something is Ellipsis or something == "n":
        state["slide"] += 1
        return show()
    elif something == "p":
        state["slide"] -= 1
        return show()
    elif something == "t":
        print("+"*84)
        return None
    elif something == "d":
        markdown.renderer.redraw()
        return show()
    elif something == "c":
        print("\n"*markdown.renderer.rows)
        return None
    elif something == "q":
        sys.exit()
    elif something == "f":
        return ask_slidenr(len(slides))
    elif isinstance(something, tuple):
        if something[0] == Ellipsis:
            return print(markdown(something[1]))

    return old_dh(something)


sys.displayhook = dh

def eh(t, v, tb):
    if isinstance(v, ZeroDivisionError):
        sys.stderr.write("17\n")
        return
    old_eh(t, v, tb)

sys.excepthook = eh

l, r, f, n, p, d, c, q, t = "lrfnpdcqt"
