# temporal-src-network Docs

The `temporal-src-network` is `python3` utility to build temporal sources network.

It can be used to download at build time all the external sources released at different points in time that may be required to build a project. It currently only supports downloading `git` repos, and it is planned to add support to download `zip`, `tar` or `raw` files.

This can be useful if you have multiple external `git` repos that are dependencies of a project and you do not want to commit their files to the host project with `git` `submodules` or sparse checkouts as it may pollute the `git` history. Instead, `temporal-src-network` can be passed manifest file(s) that contain the info on how to build the sources network, with urls of external repos (called `modules`) and required branches, tags or commits to download/checkout.

Additionally `temporal-src-network` also supports downloading more than one `versions` of external `modules` based on different branches, tags or commits of the same repo. This can be useful for cases for like a docs site which supports multiple versions so that docs of older versions in time can be viewed as well. For example, a docs site may have a `latest` docs version from the `master` branch, a `stable` docs version from the latest release tag, and a `v0.1.0` docs version from the `v0.1.0` release tag. The docs site may also have multiple external `modules`/`libraries`, each with its own multiple `versions`.

The `temporal-src-network` also supports creating symlinks for each `version` of a `module`, so that different directories/files of the external `modules`/`versions` can be symlinked to paths that are required to build the project site, ultimately creating a network of sources.

If you were to use `git` `submodules` for external repos, then the `submodules` in the host project also need to be updated whenever commits are pushed to the branches of external repos, continuously polluting the history. `git` `submodules` also do not support tags and commits. If you use `temporal-src-network`, then latest changes from specified branches can automatically be pulled from external repos at build time without having to add any new commits to the host project, unless any new release tags need to be added.

**To run `temporal-src-network` in a workflow platform, like [GitHub actions](https://github.com/features/actions), check [`stargateoss/temporal-src-network-action`](https://github.com/stargateoss/temporal-src-network-action).**

### Contents

- [Compatibility](#compatibility)
- [Releases](#releases)
- [Install](#install)
- [Current Features](#current-Features)
- [Usage](#usage)
- [Build](#build)

---

&nbsp;





## Compatibility

Requires `python3` to run.

#### Hosts

- Linux distros.
- Android version `>= 7.0` using [Termux App](https://github.com/termux/termux-app).
- Windows using [cygwin](https://cygwin.com/index.html) or [WSL](https://docs.microsoft.com/en-us/windows/wsl). *(Untested)*

## &nbsp;

&nbsp;



## Releases

The currently latest version of `temporal-src-network` is `v0.0.0`.

- [GitHub releases](https://github.com/stargateoss/temporal-src-network/releases).

---

&nbsp;





## Install

Check [install](install/index.md) docs for the **install instructions**.

---

&nbsp;





## Current Features

- Source checkout.
    - `git`
        - `https` urls. Requires a token that is set to the `"http.<src_url>.extraheader"` `git` config.
        - `ssh` urls. Requires `ssh` authentication to have already configured in the system.
- Create symlinks.

---

&nbsp;





## Usage

Check [`usage`](usage/index.md) docs for the **usage instructions**.

---

&nbsp;





## Build

Check [`build`](build/index.md) docs for the **build instructions**.

---

&nbsp;





[`actions/checkout`]: https://github.com/actions/checkout
