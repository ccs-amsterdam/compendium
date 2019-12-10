import os.path
import re

DATA_ENCRYPTED = "data/raw-private-encrypted"
DATA_PRIVATE = "data/raw-private"

SRC_PROCESSING = "src/data-processing"



def get_files(folder):
    path = os.path.abspath(os.path.join(os.getcwd(), folder))
    return os.listdir(path)


def get_headers(filename):
    for i, line in enumerate(open(filename)):
        if not line.strip():
            continue
        if not line.startswith("#"):
            break
        if i ==0 and line.startswith("#!"):
            yield "COMMAND", line[2:].strip()
        m = re.match(r"#(\w+?):(.*)", line)
        if m:
            yield m.groups()[0].strip(), m.groups()[1].strip()


def task_decrypt():
    """Decrypt private files from raw-private-encrypted"""
    for file in get_files(DATA_ENCRYPTED):
        if file.endswith(".gpg"):
            inf = os.path.join(DATA_ENCRYPTED, file)
            outf = os.path.join(DATA_PRIVATE, file.replace(".gpg", ""))

            yield {
                'name': f"Decrypt {inf} -> {outf}",
                'file_dep': [inf],
                'targets': [outf],
                'actions': [f'gpg --batch --yes -o {outf} -d {inf}'],
            }


def task_process():
    """Run processing scripts from src/data-processing"""
    for file in get_files(SRC_PROCESSING):
        fn = os.path.join(SRC_PROCESSING, file)
        headers = dict(get_headers(fn))
        if "CREATES" in headers and "COMMAND" in headers:
            target = f'data/{headers["CREATES"]}'
            inf = f'data/{headers["DEPENDS"]}' if "DEPENDS" in headers else None
            action = f"{headers['COMMAND']} {fn}"
            if headers.get("PIPE", "F")[0].lower() == "t":
                if inf:
                    action = f"{action} < {inf}"
                action = f"{action} > {target}"
            yield dict(
                targets=[target],
                name=headers.get("TITLE", f"Create {target} using {fn}"),
                actions=[action],
                file_dep=[inf] if inf else None
            )

