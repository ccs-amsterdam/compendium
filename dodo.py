import subprocess
import re
from collections import namedtuple
from pathlib import Path
import logging
from typing import Iterable, List, Tuple, Optional, NamedTuple, Dict

from doit.action import CmdAction
from doit import get_var


ROOT = Path.cwd()
DATA = ROOT/"data"
DATA_ENCRYPTED = DATA/"raw-private-encrypted"
DATA_PRIVATE = DATA/"raw-private"

SRC = ROOT/"src"
SRC_PROCESSING = SRC/"data-processing"
SRC_ANALYSIS = SRC/"analysis"

EXT_SCRIPT = {".py", ".R", ".Rmd", ".sh"}


def contained_in(parent: Path, descendant: Path) -> bool:
    if parent.is_absolute():
        descendant = descendant.absolute()
    return str(descendant.absolute()).startswith(str(parent))


class Action(NamedTuple):
    file: Path
    action: str
    targets: List[Path]
    inputs: List[Path]
    headers: Dict[str, str]


def get_files(folder: Path, suffix=None) -> List[Path]:
    if isinstance(suffix, str):
        suffix = [suffix]
    path = Path.cwd()/folder
    if not path.is_dir():
        logging.warning(f"Skipping non-existent path {path}")
        return []
    return [f for f in path.iterdir() if (f.is_file() and ((suffix is None) or (f.suffix in suffix)))]


def get_headers(file: Path) -> Iterable[Tuple[str, str]]:
    for i, line in enumerate(file.open()):
        if not line.strip():
            continue
        if not line.startswith("#"):
            break
        if i ==0 and line.startswith("#!"):
            yield "COMMAND", line[2:].strip()
        m = re.match(r"#(\w+?):(.*)", line)
        if m:
            yield m.groups()[0].strip(), m.groups()[1].strip()


def parse_files(text: str) -> List[Path]:
    if not text or not text.strip():
        return []
    return [Path(x.strip()) for x in re.split("[ ,]+", text)]


def get_actions():
    """Yield all processing and analysis scripts"""
    for file in get_files(SRC_PROCESSING, suffix=EXT_SCRIPT) + get_files(SRC_ANALYSIS, suffix=EXT_SCRIPT):
        headers = dict(get_headers(file))
        if "CREATES" in headers and "COMMAND" in headers:
            targets = parse_files(headers["CREATES"])
            inputs = parse_files(headers.get("DEPENDS"))
            # build action
            action = f"{headers['COMMAND']} {file}"
            if headers.get("PIPE", "F")[0].lower() == "t":
                if len(inputs) > 1 or len(targets) > 1:
                    raise ValueError("File {file}: Cannot use PIPE with multiple inputs or outputs")
                if inputs:
                    action = f"{action} < {inputs[0]}"
                action = f"{action} > {targets[0]}"
            if file.suffix == ".py":
                # Activate virtual environent before calling script
                action = f"(. env/bin/activate; {action})"
            action = f'{action} && echo "[OK] {file.name} completed" 1>&2'
            yield Action(file, action, targets, inputs, headers)


def task_install():
    """Install python/R dependencies as needed"""
    packrat = Path("packrat/packrat.lock")
    if packrat.is_file():
        yield {
            'name': f"Install R dependencies using {packrat}",
            'file_dep': [packrat],
            'actions': [f"Rscript -e 'if (!require(packrat)) install.packages(\"packrat\"); packrat::restore()'"]
        }
    requirements = Path("requirements.txt")
    if requirements.is_file():
        lib = Path.cwd()/"src"/"lib"
        yield {
            'name': f"Install python dependencies in virtual environment env from {requirements}",
            'file_dep': [requirements],
            'targets': ['env'],
            'actions': ["python3 -m venv env",
                        "env/bin/pip install -U pip wheel",
                        f"env/bin/pip install -r {requirements}",
                        f'export LIB=`ls env/lib`; echo "{lib}" > "env/lib/$LIB/site-packages/compendium_extra.pth"'],
            'verbosity': 2
        }


def _get_passphrase():
    if get_var('passphrase'):
        return get_var('passphrase')
    return None


def error_cannot_decrypt():
    raise Exception('Cannot decrypt files as no passphrase is given. Use `doit passphrase="Your passphrase"` to specify')

            
def task_decrypt():
    """Decrypt private files from raw-private-encrypted (provide passphrase with `doit passphrase="Your secret"`)"""
    gpg_files = get_files(DATA_ENCRYPTED, ".gpg")
    if gpg_files:
        passphrase = _get_passphrase()
        for inf in gpg_files:
            outf = DATA_PRIVATE/inf.stem
            if passphrase:
                action = f'mkdir -p {DATA_PRIVATE} &&  gpg --batch --yes --passphrase "{passphrase}" -o {outf} -d {inf}'
            else:
                action = error_cannot_decrypt

            yield {
                'name': outf,
                'file_dep': [inf],
                'targets': [outf],
                'actions': [action]
            }


def task_process():
    """Create tasks for the processing scripts in src/data-processing"""
    for action in get_actions():
            result = dict(
                basename=f"process:{action.file.name}",
                targets=action.targets,
                actions=[action.action],
            )
            if 'DESCRIPTION' in action.headers:
                result['doc'] = action.headers['DESCRIPTION']
            if action.inputs:
                result['file_dep'] = action.inputs
            else:
                result['uptodate'] = [True]  # task is up-to-date if target exists
            yield(result)


def do_encrypt(args):
    if args.files:
        files = [Path(x).resolve() for x in  args.files]
        for f in files:
            if not f.parent == DATA_PRIVATE.resolve():
                raise ValueError(f"File {f} not in {DATA_PRIVATE}, so will not be encrypted!")
    else:
        files = get_files(DATA_PRIVATE)
    for file in files:
        outfile = DATA_ENCRYPTED/f"{file.name}.gpg"
        print(f"Encrypting {file} -> {outfile}")
        cmd = ['gpg', '--yes', '--symmetric', '--batch', '--passphrase', args.passphrase, "-o", outfile, file]
        subprocess.check_call(cmd)


def document_readme():
    actions = list(get_actions())
    md = "# Data processing scripts"
    md += "\n\nThis folder contains the following scripts:\n\n"
    for action in actions:
        inputs =  ",".join(f"[{f.name}]({f})" for f in action.inputs)
        targets = ",".join(f"[{f.name}]({f})" for f in action.targets)
        md += f"- [{action.file.name}](action.file): [{inputs} -> {targets}]  \n  {action.headers.get('DESCRIPTION')}  \n  \n"
    print(md)


def document_process():
    actions = list(get_actions())
    nodes, nodemap, edges = [], {}, []

    def get_node(file):
        file = file.absolute()
        if contained_in(DATA_ENCRYPTED, file):
            shape = "box3d"
            file = file.relative_to(DATA)
        if contained_in(DATA, file):
            shape = "note"
            file = file.relative_to(DATA)
        elif contained_in(SRC_PROCESSING, file):
            shape = "cds"
            file = file.relative_to(SRC_PROCESSING)
        elif contained_in(SRC_ANALYSIS, file):
            shape = "component"
            file = file.relative_to(SRC_ANALYSIS)

        if file not in nodemap:
            name = f"n_{len(nodemap)}"
            nodemap[file] = name
            label = str(file).replace("/", "/\\n")
            nodes.append(f'\n{name} [label="{label}", shape="{shape}"];')
        return nodemap[file]

    for inf in get_files(DATA_ENCRYPTED, ".gpg"):
        outf = DATA_PRIVATE/inf.stem
        node = get_node(inf)
        node2 = get_node(outf)
        edges.append(f'\n{node} -> {node2};')

    for i, action in enumerate(actions):
        node = get_node(action.file)
        for f in action.inputs:
            node2 = get_node(f)
            edges.append(f'\n{node2} -> {node};')
        for f in action.targets:
            node2 = get_node(f)
            edges.append(f'\n{node} -> {node2};')
    nodes = "\n".join(nodes)
    edges = "\n".join(edges)
    dot = f'digraph G {{graph [rankdir="LR"]; \n{nodes}\n\n{edges}\n}}\n'
    print(dot)


def do_document(args):
    if args.what == "readme":
        document_readme()
    elif args.what == "process":
        document_process()


if __name__ == '__main__':
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description = "Doit file for data compendium. Run `doit` to generate files and results rather than running this script. As author, you can use this script to generate documentation or encrypt private files. ")

    subparsers = parser.add_subparsers(help='Action to perform')

    encrypt = subparsers.add_parser('encrypt', help='Encrypt private files')
    encrypt.add_argument('passphrase', help='Passphrase for encryption')
    encrypt.add_argument('files', nargs="*", help='Files to encrypt (if blank, encrypt all private files)')
    encrypt.set_defaults(func=do_encrypt)

    encrypt = subparsers.add_parser('document', help='Generate documentation')
    encrypt.add_argument('what', help='Which documentation to generate', choices=['process', 'readme'])
    encrypt.set_defaults(func=do_document)

    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        args.func(args)
