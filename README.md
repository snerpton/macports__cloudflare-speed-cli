[![CI](https://github.com/snerpton/macports__cloudflare-speed-cli/actions/workflows/update-macports-portfile.yml/badge.svg)](https://github.com/snerpton/macports__cloudflare-speed-cli/actions/workflows/update-macports-portfile.yml)
[![MacPorts](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fports.macports.org%2Fapi%2Fv1%2Fports%2Fcloudflare-speed-cli%2F&query=%24.version&prefix=v&label=MacPorts&color=blue)](https://ports.macports.org/port/cloudflare-speed-cli/)


# macports__cloudflare-speed-cli

Automation for maintaining the [MacPorts](https://www.macports.org/) Portfile for [cloudflare-speed-cli](https://github.com/kavehtehrani/cloudflare-speed-cli), a Rust-based CLI tool for running internet speed tests via Cloudflare's speed test service.

When a new version of `cloudflare-speed-cli` is released, this repository's GitHub Actions workflow detects it, regenerates the Portfile with updated checksums and Cargo dependency data, pushes a branch to a MacPorts fork, and publishes a GitHub Release containing a ready-to-test zip of the Portfile.

---

## Repository structure

```
.github/
  workflows/
    update-macports-portfile.yml   # The automation workflow
  scripts/
    gen_cargo_crates.py            # Generates the cargo.crates block from Cargo.lock
    update_portfile.py             # Rewrites the Portfile in-place
README.md
```

---

## How it works

The workflow runs on a daily schedule and can also be triggered manually. It performs the following steps:

1. **Fetches the target release** from `kavehtehrani/cloudflare-speed-cli` — either a specific version supplied as a manual input, or the latest release.
2. **Checks out your macports-ports fork** and reads the version currently in the Portfile. If it already matches the target version, the workflow exits early with no changes made.
3. **Downloads the source tarball** for the release and computes the `sha256`, `rmd160`, and `size` checksums required by MacPorts.
4. **Generates the `cargo.crates` block** by extracting the source, running `cargo fetch` to resolve all dependencies, and parsing `Cargo.lock` to produce the full list of crate checksums in MacPorts format.
5. **Rewrites the Portfile** with the new version, checksums, and `cargo.crates` block.
6. **Pushes a branch** (`update-cloudflare-speed-cli-{version}`) to your macports-ports fork. If the branch already exists from a previous run it is overwritten.
7. **Creates a GitHub Release** in this repository (tagged `cloudflare-speed-cli-{version}`) and attaches a zip of the Portfile in the correct MacPorts directory structure for local testing.

---

## Setup

### 1. Fork macports-ports

Fork [macports/macports-ports](https://github.com/macports/macports-ports) into your GitHub account. This is where the workflow will push Portfile update branches.

### 2. Create a Personal Access Token (PAT)

The workflow needs permission to push branches to your macports-ports fork. Create a fine-grained PAT scoped to that fork only with the following permissions:

| Permission | Level |
|---|---|
| Contents | Read and write |

### 3. Configure repository secrets

In this repository go to **Settings → Secrets and variables → Actions → Secrets** and add:

| Secret | Value |
|---|---|
| `MACPORTS_FORK_TOKEN` | The PAT created in step 2 |

### 4. Configure repository variables

In this repository go to **Settings → Secrets and variables → Actions → Variables** and add:

| Variable | Example value | Description |
|---|---|---|
| `MACPORTS_FORK_REPO` | `snerpton/macports-ports` | Your macports-ports fork |
| `PORTFILE_PATH` | `net/cloudflare-speed-cli/Portfile` | Path to the Portfile within the fork |

---

## Running the workflow

### Scheduled runs

The workflow runs automatically every day at 10:00 UTC. If no new release has been published upstream it exits early without making any changes.

### Manual runs

Go to **Actions → Update MacPorts Portfile for cloudflare-speed-cli → Run workflow**.

There is one optional input:

| Input | Description |
|---|---|
| `release_tag` | The upstream release to target, e.g. `v1.2.3` or `1.2.3`. Leave blank to use the latest release. |

---

## Outputs

### Branch on your macports-ports fork

Each successful run pushes a branch named `update-cloudflare-speed-cli-{version}` to your fork. From there you can review the changes and open a pull request against upstream `macports/macports-ports` when you are satisfied.

### GitHub Release with zip artifact

A release is created in this repository tagged `cloudflare-speed-cli-{version}`, with a zip attached named `cloudflare-speed-cli-portfile-{version}.zip`. The zip contains the Portfile in the correct MacPorts directory layout:

```
net/
  cloudflare-speed-cli/
    Portfile
```

To test locally, download and unzip the artifact, then install directly from the Portfile:

```sh
sudo port install /path/to/net/cloudflare-speed-cli/Portfile
```

---

## Script reference

### `gen_cargo_crates.py`

```
python3 gen_cargo_crates.py <path/to/Cargo.lock>
```

Parses a `Cargo.lock` file and produces a MacPorts-formatted `cargo.crates` block. Only packages sourced from the `crates.io` registry (i.e. those with a `registry+` source URL) are included. The output is written to `/tmp/cargo_crates.txt` and also printed to stdout. Crates are sorted alphabetically and aligned for readability.

### `update_portfile.py`

```
python3 update_portfile.py <portfile> <version> <sha256> <rmd160> <size>
```

Rewrites a Portfile in-place, making four changes:

1. Updates the version on the `github.setup` line
2. Resets `revision` to `0`
3. Replaces the `checksums` block with the newly computed values
4. Replaces the `cargo.crates` block with the output of `gen_cargo_crates.py`

---

## Related

- [cloudflare-speed-cli](https://github.com/kavehtehrani/cloudflare-speed-cli) — the upstream project
- [macports/macports-ports](https://github.com/macports/macports-ports) — the upstream MacPorts ports tree
- [MacPorts Guide — Portfile development](https://guide.macports.org/#development)
