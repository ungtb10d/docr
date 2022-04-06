# coding: utf-8

import sys
import subprocess
from invoke import task
from pathlib import Path


REPO_HOME = Path.cwd()
PYTHON_TARGETS = [
    f"3.{x}-{arch}"
    for x in range(8, 11)
    for arch in ("32", "64")
]



def get_python_path(py_ident):
    try:
        return subprocess.check_output([
            "py",
            f"-{py_ident}",
            "-c",
            "import sys;print(sys.executable)"
        ]).decode(sys.getfilesystemencoding())
    except subprocess.CalledProcessError:
        pass


@task
def build_wheels(c, release=False, strip=False):
    i_args = {
        f'"{py_path}"': "i686-pc-windows-msvc" if ident.endswith("32") else "x86_64-pc-windows-msvc"
        for ident in PYTHON_TARGETS
        if (py_path := get_python_path(ident))
    }
    with c.cd(REPO_HOME / "docrpy"):
        for (pypath, arch) in i_args.items():
            build_command = " ".join([
                "maturin build",
                "--release" if release else "",
                "--strip" if strip else "",
                f"-i {pypath}"
            ])
            c.run(
                build_command,
                env={'CARGO_BUILD_TARGET': arch}
            )


@task
def upload_wheels(c):
    with c.cd(REPO_HOME):
        c.run(r'twine upload  "./target/wheels/*" --non-interactive --skip-existing')
