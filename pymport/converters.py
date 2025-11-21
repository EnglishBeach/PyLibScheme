import subprocess
from pathlib import Path


def use_pydeps(lib: Path, workdir: Path) -> Path:
    out = workdir / "out.dot"
    cmd = f'pydeps "{lib.resolve()}" --dot-output "{out.name}" --show-dot --noshow --include-missing --only {lib.stem}'
    sp = subprocess.run(
        cmd,
        shell=True,
        cwd=workdir,
        capture_output=True,
        check=False,
    )
    if sp.returncode:
        raise RuntimeError("\n" + sp.stderr.decode())
    return out


def dot2gml(dot: Path, workdir: Path) -> Path:
    out = workdir / "out.gml"
    cmd = f'gv2gml -o "{out.name}" "{dot.resolve()}"'
    sp = subprocess.run(
        cmd,
        shell=True,
        cwd=workdir,
        capture_output=True,
        check=False,
    )
    if sp.returncode:
        raise RuntimeError("\n" + sp.stderr.decode())
    return out


def use_pyreverse(lib: Path, workdir: Path):
    out = workdir / "classes.dot"
    cmd = f'pyreverse "{lib.resolve()}" -f ALL -k --colorized --source-roots "{lib.resolve()}" -A -S'
    sp = subprocess.run(
        cmd,
        shell=True,
        cwd=workdir,
        capture_output=True,
        check=False,
    )
    if sp.returncode:
        raise RuntimeError("\n" + sp.stderr.decode())

    (workdir / "packages.dot").unlink()
    return out
