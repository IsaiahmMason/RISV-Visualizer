# C-to-RISC-V Visualizer (Demo)

A web tool that compiles small C programs to RV32I and shows the assembly
and decoded machine code side by side.

## Status
Working: compile (-O0 / -O2), assembly view, hex/binary view, RV32I decoder,
error reporting, 18 automated tests.
Not yet built: linked line highlighting, color-coded field display,
example-program dropdown.

## Requirements
- Ubuntu / WSL (tested on Ubuntu 22.04)
- `gcc-riscv64-unknown-elf` 10.2.0 and `binutils-riscv64-unknown-elf` 2.35.1
- Python 3.10+ with `python3-venv`

```bash
sudo apt install gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf python3-venv
```

## Run
```bash
make setup
make run
```
Open http://127.0.0.1:5000

## Test
```bash
make test
```

## Supported C subset
Small, self-contained programs. `*`, `/`, `%` fail to link because RV32I has
no multiply/divide and no runtime library is linked (`-nostdlib`).
Use `+`, `-`, and shifts. `volatile` keeps `-O2` from folding everything
into a constant.

## Notes
Backend is Python/Flask rather than C/Mongoose as the design doc proposed.
Design doc: docs/DESIGN.md

## WSL troubleshooting
If apt/pip/git hang: `sudo ip link set dev eth0 mtu 1350`