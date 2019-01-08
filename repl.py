import sys
from collections.abc import Callable, Hashable
import trio
from markdown import markdown

old_dh = sys.displayhook

state = {"language": "english", "slide": -1}
mode = "normal"

bindings = {"l": ("language", ["german", "english"])}
with open("slides.md") as f:
    slides = f.read().split("\n====\n")


def show():
    nr = state["slide"]
    if nr >= len(slides):
        state["slide"] -= 1
    print(markdown(slides[state["slide"]]))
    print(f"[{state['slide']+1}/{len(slides)}]".rjust(markdown.renderer.columns))


def ask(key, choices, phrase=None):
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
    if isinstance(mode, Callable):
        return mode(something)
    elif isinstance(something, Hashable) and something in bindings:
        return ask(*bindings[something])
    elif something is Ellipsis or something == "n":
        state["slide"] += 1
        return show()
    elif something == "p":
        state["slide"] -= 1
        return show()
    elif something == "r":
        markdown.renderer.redraw()
        return show()
    elif something == "f":
        return ask_slidenr(len(slides))
    elif isinstance(something, tuple):
        if something[0] == Ellipsis:
            return print(markdown(something[1]))

    return old_dh(something)


sys.displayhook = dh

l, r, f, n, p = "lrfnp"
