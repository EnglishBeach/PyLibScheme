import shutil
import tempfile
from pathlib import Path

from pylibscheme import converters, files, parser, tools


def create_import_graph(lib_path: str, out_file: str = "out_pkg.gml") -> Path:
    """
    Create import graph from Python library

    :param lib_path: Library folder path
    :param out_file: Output file path, defaults to "out_pkg.gml"
    :return: Import graph `.gml` file path
    """
    out = Path(out_file)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        new_lib, inits = files.create_inits(lib=Path(lib_path), workdir=tmp)
        dot_file = converters.use_pydeps(lib=new_lib, workdir=tmp)
        gml = converters.dot2gml(dot=dot_file, workdir=tmp)

        g = parser.Graph.load(file=gml)
        for n in g.nodes:
            n.name = n.label if n.label else n.name
            label = n.label.split(".")[-1] if n.label else n.name.split(".")[-1]
            label = label.replace('"', "")
            n.label = f'"{label}"'

        g = tools.clusterize(g, ter_groups=False)
        g = tools.colorize(g)
        g = tools.prune(g, inits)

        save_file = tmp / out.name
        g.save(file=save_file)
        shutil.copy(src=save_file, dst=out_file)
    return out


def create_class_graph(lib_path: str, out_file: str = "out_cls.gml"):
    """
    Classes graph path

    :param lib_path: Library folder path
    :param out_file: Output file path, defaults to "out_cls.gml"
    :return: Classes graph `.gml` file path
    """
    out = Path(out_file)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        new_lib, inits = files.create_inits(lib=Path(lib_path), workdir=tmp)
        dot = converters.use_pyreverse(lib=new_lib, workdir=tmp)
        gml = converters.dot2gml(dot=dot, workdir=tmp)

        g = parser.Graph.load(file=gml)
        for n in g.nodes:
            name = ".".join(n.name.replace('"', "").split(".")[:-1])
            n.name = f'"{new_lib.stem}.{name}"'

        g = tools.clusterize(g, ter_groups=True)

        save_file = tmp / out.name
        g.save(file=save_file)
        shutil.copy(src=save_file, dst=out)
        return out
