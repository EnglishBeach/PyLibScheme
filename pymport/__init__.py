import shutil
import tempfile
from pathlib import Path

from pymport import converters, files, parser, tools


def create_graph(lib_path: str, out_file: Path = Path("out.gml")) -> Path:
    lib = Path(lib_path)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        new_lib, inits = files.create_inits(lib=lib, workdir=tmp)
        dot_file = converters.use_pydeps(lib=new_lib, workdir=tmp)
        gml = converters.dot2gml(dot=dot_file, workdir=tmp)

        g = parser.Graph.load(file=gml)

        for n in g.nodes:
            n.name = n.label if n.label else n.name

        g = tools.clusterize(g)
        g = tools.colorize(g)
        g = tools.prune(g, inits)

        save_file = tmp / out_file.name
        g.save(file=save_file)
        shutil.copy(src=save_file, dst=out_file)
    return out_file
