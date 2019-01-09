import os
import builtins
import re
import colorful
import mistune
from PIL import Image, ImageDraw, ImageFont
import numpy as np


colorful.use_style("solarized")

ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def nonempty(text):
    return text.strip()


class TerminalRenderer(mistune.Renderer):
    def __init__(self):
        self.redraw()
        super().__init__()

    def wrapped(self, text, modifier=0):
        """Uggh... control sequences."""
        line, count = "", 0
        for word in text.split():
            clean = ansi_escape.sub("", word)
            if len(clean) + 1 + count <= self.columns + modifier:
                line += (" " if line else "") + word
                count += len(clean) + 1
            else:
                yield line
                line = word
                count = len(clean)
        if line:
            yield line

    def header(self, text, level, raw=None):
        for size in [72, 48, 24, 20, 18, 17, 16, 15, 14, 13, 12, 11, 10]:
            myfont = ImageFont.truetype("Verdana", size)
            size = myfont.getsize(text)
            img = Image.new("L", size, "black")
            draw = ImageDraw.Draw(img)
            draw.text((0, 0), text, "white", font=myfont)
            pixels = np.array(img, dtype=np.uint8) // 32
            chars = np.array(
                [" ", " ", "░", "░", "▒", "▒", "▓", "█"], dtype="U1"
            )[pixels]
            lines = list(
                filter(
                    nonempty, chars.view("U" + str(chars.shape[1])).flatten()
                )
            )
            if (
                max(len(line) for line in lines) > self.columns
                or len(lines) > self.rows
            ):
                continue
            return "\n".join(lines) + "\n"
        return text.upper() + "\n\n"

    def redraw(self):
        rows, columns = map(int, os.popen("stty size", "r").read().split())
        self.rows = rows
        self.columns = columns

    def list(self, body, ordered=True):
        return body

    def list_item(self, text):
        return "· {}\n".format(text)

    def block_quote(self, text):
        return "> {}\n".format("\n  ".join(self.wrapped(text, modifier=-2)))

    def paragraph(self, text):
        return "\n".join(self.wrapped(text)) + "\n"

    def emphasis(self, text):
        return colorful.italic(text)

    def double_emphasis(self, text):
        return colorful.bold_red(text)

    def link(self, link, title, content):
        if link:
            return "{} <{}>".format(colorful.underlined_blue(content), link)
        else:
            return colorful.underlined_blue(content)

    def hrule(self):
        return "\n{}\n".format("—" * self.columns)

    def block_code(self, text, lang=None):
        if lang and lang.startswith("exec"):
            bindings = {}
            exec(text, bindings)
            for key, value in bindings.items():
                if key == "__builtins__":
                    continue
                setattr(builtins, key, value)
        if lang and lang.endswith("hidden"):
            return ""
        else:
            return text

    def codespan(self, text):
        return colorful.cyan(text)


renderer = TerminalRenderer()
markdown = mistune.Markdown(renderer=renderer)
