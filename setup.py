from contextlib import suppress
from setuptools import setup, Command
from setuptools.command.build import build
from pathlib import Path
import subprocess as sp
import shlex
import logging
from shutil import which

log = logging.getLogger("protoc")

proto_path = (Path(__file__).parent / "protos").absolute()
protos = [str(p) for p in proto_path.rglob("*.proto")]


protoc = which("protoc")
if protoc is None:
    raise RuntimeError("protoc not found... should be installed automatically via pyproject!")


class Protoc(Command):
    """Run protoc"""
    user_options = []
    editable_mode = False

    description = "Compile .proto files to python sources"

    def initialize_options(self):
        self.bdist_dir = None

    def finalize_options(self):
        with suppress(Exception):
            self.bdist_dir = Path(self.get_finalized_command("bdist_wheel").bdist_dir)

    def run(self):
        log.info("Found the following proto definitions: %s", protos)
        log.info("Using protoc: %s", protoc)

        if self.editable_mode:
            log.info("Editable install, using src for output of generated proto code")
            out = "./src/"
        else:
            log.info("Normal installation, using wheel dir for output of generate proto code")
            self.bdist_dir.mkdir(parents=True, exist_ok=True)
            out = self.bdist_dir

        cmd = [protoc, f"--python_out={out}", "-I", str(proto_path), *protos] 
        log.info("Running '%s'", shlex.join(cmd))
        sp.run(cmd, check=True)

class ProtocBuild(build):
    sub_commands = [('protoc', None)] + build.sub_commands

setup(cmdclass={"build": ProtocBuild, "protoc": Protoc})
