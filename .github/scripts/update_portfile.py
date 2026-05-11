#!/usr/bin/env python3
"""
update_portfile.py  <portfile>  <version>  <sha256>  <rmd160>  <size>

Rewrites a MacPorts Portfile in-place:
  1. Updates the version in the `github.setup` line
  2. Resets `revision` to 0
  3. Replaces the `checksums` block
  4. Replaces the `cargo.crates` block (read from /tmp/cargo_crates.txt)
"""
import re
import sys
import pathlib

portfile_path = pathlib.Path(sys.argv[1])
new_version   = sys.argv[2]
new_sha256    = sys.argv[3]
new_rmd160    = sys.argv[4]
new_size      = sys.argv[5]

text = portfile_path.read_text()

# 1. Update github.setup version (4th whitespace-separated token on the line)
text = re.sub(
    r'(^github\.setup\s+\S+\s+\S+\s+)\S+',
    lambda m: m.group(1) + new_version,
    text, flags=re.MULTILINE
)

# 2. Reset revision to 0
text = re.sub(r'^(revision\s+)\d+', r'\g<1>0', text, flags=re.MULTILINE)

# 3. Replace the checksums block (continuation lines included)
new_checksums = (
    "checksums               ${distname}${extract.suffix} \\\n"
    f"                        rmd160  {new_rmd160} \\\n"
    f"                        sha256  {new_sha256} \\\n"
    f"                        size    {new_size}\n"
)
text = re.sub(
    r'^checksums\b.*?(?=^\S|\Z)',
    new_checksums + "\n",
    text, flags=re.MULTILINE | re.DOTALL
)

# 4. Replace the cargo.crates block
cargo_crates_new = pathlib.Path("/tmp/cargo_crates.txt").read_text().rstrip()
text = re.sub(
    r'^cargo\.crates\b.*?(?=^\S|\Z)',
    cargo_crates_new + "\n\n",
    text, flags=re.MULTILINE | re.DOTALL
)

portfile_path.write_text(text)
print("Portfile updated successfully.")
