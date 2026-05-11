#!/usr/bin/env python3
"""
gen_cargo_crates.py  <path/to/Cargo.lock>

Reads a Cargo.lock file and writes a MacPorts-style `cargo.crates` block to
/tmp/cargo_crates.txt, ready to be spliced into a Portfile.
"""
import re
import sys
import pathlib

def spaceBetweenPackageAndVersion(packageName, version):
  stdFullWidth = 38
  usedSpace = len(packageName) + len(version)
  requiredSpace = stdFullWidth - usedSpace
  return requiredSpace * " "

lock_path = pathlib.Path(sys.argv[1])
lock = lock_path.read_text()

blocks = re.split(r'\n\[\[package\]\]', "\n" + lock)
crates = []
for block in blocks[1:]:
    name     = re.search(r'name\s*=\s*"([^"]+)"', block)
    version  = re.search(r'version\s*=\s*"([^"]+)"', block)
    source   = re.search(r'source\s*=\s*"([^"]+)"', block)
    checksum = re.search(r'checksum\s*=\s*"([^"]+)"', block)
    if name and version and source and checksum:
        if source.group(1).startswith("registry+"):
            crates.append((name.group(1), version.group(1), checksum.group(1)))

if not crates:
    print("ERROR: no registry crates found in Cargo.lock", file=sys.stderr)
    sys.exit(1)

crates.sort()
lines = ["cargo.crates \\"]
for i, (n, v, c) in enumerate(crates):
    sep = " \\" if i < len(crates) - 1 else ""
    lines.append(f"    {n}{spaceBetweenPackageAndVersion(n,v)}{v}  {c}{sep}")

output = "\n".join(lines) + "\n"
pathlib.Path("/tmp/cargo_crates.txt").write_text(output)
print(output, end="")
