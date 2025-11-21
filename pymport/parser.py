from pathlib import Path
from typing import Optional

from pydantic import BaseModel, model_validator


class Entry(BaseModel):
    _entry_name = "entry"

    @classmethod
    def parse(cls, strings: list[str]):
        fields = {}

        i = strings.pop(0)
        while i.strip() != "]":
            title, data = i.split()
            if data.strip() == "[":
                data = CLASS_MAP[title].parse(strings)

            fields[title] = data
            i = strings.pop(0)
        return cls(**fields)

    def __str__(self):
        data = []
        for key, val in dict(self).items():
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


CLASS_MAP: dict[str, type[Entry]] = {}


def mapped(cls):
    CLASS_MAP.update({cls._entry_name.default: cls})
    return cls


@mapped
class Graphics(Entry):
    _entry_name = "graphics"

    hasFill: Optional[int] = None
    type: Optional[str] = None
    fill: Optional[str] = None
    targetArrow: Optional[str] = None
    sourceArrow: Optional[str] = None


@mapped
class LGraphics(Entry):
    _entry_name = "LabelGraphics"

    text: Optional[str] = None
    fontColor: Optional[str] = None
    fontSize: Optional[int] = None
    fontName: Optional[str] = None


_text_map = {"\\n": "", "\\.": "."}


@mapped
class Node(Entry):
    _entry_name = "node"

    id: int
    gid: Optional[int] = None
    isGroup: Optional[int] = None

    name: str
    label: Optional[str] = None

    graphics: Optional[Graphics] = None
    LabelGraphics: Optional[LGraphics] = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__.upper()} {self.id} : {self.label}>"

    @model_validator(mode="after")
    def validator(self):
        label = _replace(self.label, _text_map) if self.label else self.name
        label = label.replace('"', "")
        self.label = f'"{label}"'

        self.name = self.name if self.name else "empty"
        self.LabelGraphics = None
        return self

    @property
    def norm(self):
        return self.name.replace('"', "")


@mapped
class Edge(Entry):
    _entry_name = "edge"

    id: int
    source: int
    target: int
    fillcolor: Optional[str] = None
    minlen: Optional[str] = None
    weight: Optional[str] = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__.upper()} {self.id} : {self.source} -> {self.target}>"


class Graph(BaseModel):
    title_data: list[str]
    entries: list[Entry]

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
            entries.append(CLASS_MAP[title].parse(lines))
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

    @property
    def nodes(self) -> list[Node]:
        return [i for i in self.entries if isinstance(i, Node)]

    @property
    def edges(self) -> list[Edge]:
        return [i for i in self.entries if isinstance(i, Edge)]


def _replace(string: str, repl_map: dict[str, str]):
    a = string
    for key, val in repl_map.items():
        a = a.replace(key, val)
    return a
