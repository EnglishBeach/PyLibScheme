from __future__ import annotations

import copy
from pathlib import Path
from typing import Optional

_text_map = {"\\n": "", "\\.": "."}

_CLASS_MAP: dict[str, type[Entry]] = {}


class Entry:
    """Graph entry"""

    _entry_name = "entry"

    @classmethod
    def parse(cls, strings: list[str]):
        """
        Parse line

        :param strings: String
        :return: Entry
        """
        fields = {}

        i = strings.pop(0)
        while i.strip() != "]":
            title, data = i.split()

            if data.strip() == "[":
                data = _CLASS_MAP[title].parse(strings)

            fields[title] = data
            i = strings.pop(0)
        return cls(**fields)

    def __str__(self):
        data = []
        for key, val in self.__dict__.items():
            if val is None:
                continue
            elif isinstance(val, Entry):
                key = ""
            data.append(f"{key} {val}")

        return "\n".join(
            (
                f"{self._entry_name} [",
                *data,
                "]",
            )
        )


def mapped(cls):
    """
    Map entry: entry name in graph
    """
    _CLASS_MAP.update({cls._entry_name: cls})
    return cls


@mapped
class Graphics(Entry):
    _entry_name = "graphics"

    def __init__(
        self,
        hasFill: Optional[int] = None,
        type: Optional[str] = None,
        fill: Optional[str] = None,
        targetArrow: Optional[str] = None,
        sourceArrow: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.hasFill = int(hasFill) if hasFill else hasFill
        self.type = type
        self.fill = fill
        self.targetArrow = targetArrow
        self.sourceArrow = sourceArrow


@mapped
class LGraphics(Entry):
    _entry_name = "LabelGraphics"

    def __init__(
        self,
        text: Optional[str] = None,
        fontColor: Optional[str] = None,
        fontSize: Optional[int] = None,
        fontName: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.text = text
        self.fontColor = fontColor
        self.fontSize = int(fontSize) if fontSize else None
        self.fontName = fontName


@mapped
class Node(Entry):
    _entry_name = "node"

    def __init__(
        self,
        id: int,
        name: str,
        gid: Optional[int] = None,
        isGroup: Optional[int] = None,
        label: Optional[str] = None,
        graphics: Optional[Graphics] = None,
        LabelGraphics: Optional[LGraphics] = None,
        **kwargs,
    ) -> None:
        self.id = int(id)
        self.gid = int(gid) if gid else None
        self.isGroup = int(isGroup) if isGroup else None
        self.name = name
        self.label = label
        self.graphics = graphics
        self.LabelGraphics = LabelGraphics

        label = _replace(self.label, _text_map) if self.label else self.name
        label = label.replace('"', "")
        self.label = f'"{label}"'

        self.name = self.name if self.name else "empty"
        self.LabelGraphics = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__.upper()} {self.id} : {self.label}>"

    @property
    def norm(self):
        return self.name.replace('"', "")


@mapped
class Edge(Entry):
    _entry_name = "edge"

    def __init__(
        self,
        id: int,
        source: int,
        target: int,
        fillcolor: Optional[str] = None,
        minlen: Optional[str] = None,
        weight: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.id = int(id)
        self.source = int(source)
        self.target = int(target)
        self.fillcolor = fillcolor
        self.minlen = minlen
        self.weight = weight

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__.upper()} {self.id} : {self.source} -> {self.target}>"


class Graph:
    """Graph representation"""

    @property
    def nodes(self) -> list[Node]:
        return [i for i in self.entries if isinstance(i, Node)]

    @property
    def edges(self) -> list[Edge]:
        return [i for i in self.entries if isinstance(i, Edge)]

    def __init__(
        self,
        title_data: list[str],
        entries: list[Entry],
    ) -> None:
        self.title_data = title_data
        self.entries = entries

    @classmethod
    def load(cls, file: Path):
        lines = file.read_text().split("\n")

        title_data = []
        i = lines.pop(0)
        while "node" not in i:
            title_data.append(i)
            i = lines.pop(0)
        lines.insert(0, i)

        entries = []
        i = lines.pop(0)
        while i.strip() != "]":
            title, data = i.split()
            entries.append(_CLASS_MAP[title].parse(lines))
            i = lines.pop(0)

        return Graph(
            title_data=title_data,
            entries=entries,
        )

    def save(self, file: Path):
        file.write_text(
            "\n".join(
                (
                    "\n".join(self.title_data),
                    "\n".join(str(i) for i in self.entries),
                    "]",
                )
            )
        )

    def copy(self) -> Graph:
        return copy.deepcopy(self)


def _replace(string: str, repl_map: dict[str, str]):
    """
    Replace characters in string

    :param string: String
    :param repl_map: Replace map
    :return: Replaced string
    """
    a = string
    for key, val in repl_map.items():
        a = a.replace(key, val)
    return a
