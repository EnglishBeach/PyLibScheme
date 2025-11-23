import shutil
from pathlib import Path


def create_inits(lib: Path, workdir: Path) -> tuple[Path, list[str]]:
    """
    Create empty `__init__.py` files in library folder recursively

    :param lib: Library path
    :param workdir: Workdir
    :return: Library path and added `__init__.py` files
    """
    out = workdir / lib.stem
    shutil.copytree(src=lib, dst=out)

    prune_list = _create_inits(path=out)

    prune_names = [
        str(i.relative_to(out.parent)).split("/__init__.py")[0].replace("/", ".")
        for i in prune_list
    ]

    return (out, prune_names)


def _create_inits(path: Path) -> list[Path]:
    """
    Recurrent create `__init__.py` function

    :param path: Library path
    :return: Added `__init__.py` files
    """
    add_list = []
    add = False
    init_exists = False
    for i in path.iterdir():
        if i.is_dir():
            add_list.extend(_create_inits(i))
        elif i.name == "__init__.py" and i.read_text().strip() == "":
            init_exists = True
            add_list.append(i)
        elif i.name == "__init__.py":
            init_exists = True
        elif i.suffix == ".py":
            add = True

    if add and (not init_exists):
        init = path / "__init__.py"
        init.write_text("")
        add_list.append(init)
    return add_list
