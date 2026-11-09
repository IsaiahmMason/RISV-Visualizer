import json
import os
import re
import signal
import subprocess
import sys
import tempfile

GCC = "riscv64-unknown-elf-gcc"
OBJDUMP = "riscv64-unknown-elf-objdump"

ALLOWED_OPT = {"O0", "O2"}          # Sec 9.2: no arbitrary flags
MAX_SOURCE_BYTES = 16 * 1024        # Sec 8.1: source-size limit
TIMEOUT_S = 10                      # Sec 9.5: execution time limit
MAX_OUTPUT_CHARS = 256 * 1024       # Sec 9.6: output limit

class RequestError(ValueError):
    """Invalid request (HTTP 400 later)."""

def _run(args, cwd):
    # Sec 9.1: args list, never a shell. Sec 9.9: minimal environment.
    env = {"PATH": os.environ.get("PATH", ""), "LC_ALL": "C", "TMPDIR": cwd}
    proc = subprocess.Popen(
        args, cwd=cwd, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True,      # lets us kill gcc's child processes too
    )
    try:
        out, err = proc.communicate(timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        return -1, "", "Compilation timed out."
    return proc.returncode, out[:MAX_OUTPUT_CHARS], err[:MAX_OUTPUT_CHARS]

def compile_source(source, optimization):
    # Sec 8.2: validate the request
    if not isinstance(source, str) or not source.strip():
        raise RequestError("source must be a non-empty string")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise RequestError("source exceeds size limit")
    if optimization not in ALLOWED_OPT:
        raise RequestError("optimization must be one of: O0, O2")

    # Sec 9.3: isolated temp workspace, always removed
    with tempfile.TemporaryDirectory(prefix="riscv_") as tmp:
        with open(os.path.join(tmp, "source.c"), "w") as f:
            f.write(source)

        # Sec 4.2 flags (+ linker args so the ELF has a known layout)
        code, _, err = _run([
            GCC, "-march=rv32i", "-mabi=ilp32", "-g", "-" + optimization,
            "-ffreestanding", "-nostdlib", "-mno-relax",
            "-Wl,-Ttext=0x10000", "-Wl,-e,main",
            "-o", "out.elf", "source.c",
        ], tmp)

        # Sec 8.4: don't leak server paths
        err = err.replace(tmp + "/", "")
        diagnostics = [l for l in err.splitlines() if l.strip()]

        if code != 0:
            return {"success": False, "diagnostics": diagnostics}

        code, out, err2 = _run(
            [OBJDUMP, "-d", "-l", "-M", "no-aliases", "out.elf"], tmp)
        if code != 0:
            return {"success": False,
                    "diagnostics": ["Could not disassemble compiled output."]}

    assembly, instructions = [], []
    line = None                      # Sec 8.3: None -> JSON null, never 0
    for raw in out.splitlines():
        m = re.match(r"^.*source\.c:(\d+)", raw)
        if m:
            line = int(m.group(1))   # one-based, matches the editor
            continue
        m = re.match(r"^\s*([0-9a-f]+):\s+([0-9a-f]{8})\s+(.*)$", raw)
        if m:
            addr = int(m.group(1), 16)
            word = int(m.group(2), 16)
            assembly.append({
                "address": addr,
                "text": re.sub(r"\s+", " ", m.group(3)).strip(),
                "source_line": line,
            })
            instructions.append({
                "address": addr,
                "hex": f"0x{word:08x}",
                "binary": f"{word:032b}",
                "source_line": line,
            })

    return {"success": True, "assembly": assembly,
            "instructions": instructions, "diagnostics": diagnostics}

if __name__ == "__main__":
    path, opt = sys.argv[1], sys.argv[2]
    with open(path) as f:
        print(json.dumps(compile_source(f.read(), opt), indent=2))