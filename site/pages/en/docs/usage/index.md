# Usage

The `temporal-src-network` expects the `manifest` files containing the [`config`] on how to build the sources network in [`YAML` `1.2.0`](https://yaml.org/spec/1.2.0) or [`JSON`](https://docs.python.org/3.7/library/json.html) format. `YAMl` is the preferred format since its a better configuration language than `JSON`, specially due to support for comments and splitting strings on multiple lines.

Check [`config`] docs for info on what `manifest` files should contain.

### Contents

- [Help](#help)
- [Examples](#examples)
- [Command Types](#command-types)

---

&nbsp;





## Help

```
temporal-src-network command is used to build temporal sources network.

Usage:
  temporal-src-network [options] command_type manifests...

positional arguments:
  command_type          command type to run:
                          'setup' - setup project and modules
                          'remove' - remove project and modules
  manifests             one or more paths to manifest file(s)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v                    increase log level,
                        pass one or more times for 'debug', 'verbose' or `vverbose',
                        (default: 'normal')
  -q, --quiet           set log level to 'off',
                        (default: false)
  --manifests-format MANIFESTS_FORMAT
                        force consider manifest to be in desired format,
                        (default: use file extension, values: 'yaml', 'yml' or 'json')

The 'command_type' and 'manifests' arguments must be passed.

The manifests must either be in yaml or json format with the respective file extension,
unless the '--manifests-format' argument is passed. If manifest is a
fd path, then it will be assumed to be in yaml format unless '--manifests-format'
argument is passed.
```

---

&nbsp;





## Examples

### Setup single project

```shell
temporal-src-network setup /path/to/manifest.yaml
```

&nbsp;



### Setup multiple projects

```shell
temporal-src-network setup /path/to/manifest1.yaml /path/to/manifest2.yaml
```

&nbsp;



### Remove single project

```shell
temporal-src-network remove /path/to/manifest.yaml
```

&nbsp;



### Setup single project with vverbose logging

```shell
temporal-src-network -vvv setup /path/to/manifest.yaml
```

&nbsp;



### Setup single project with manifest passed with process substitution

[Process Substitution](https://en.wikipedia.org/wiki/Process_substitution) can be used to pass the manifest to `temporal-src-network` if the calling shell supports it, like [`bash`](https://www.gnu.org/software/bash). This can be useful if manifest does not exist in a physical file or you want to dynamically generate the manifest, like in [GitHub actions](https://github.com/features/actions) workflow.

The following is the format for passing text of a yaml `manifest`.

```shell
temporal-src-network -vv --manifests-format=yaml setup <(cat <<'MANIFEST_EOF'
<manifest>
MANIFEST_EOF
)
```

The following is the process substitution part.

```shell
<(

)
```

Inside it there is a [Here Document](https://en.wikipedia.org/wiki/Here_document#Unix_shells) that is passed to `cat` as `stdin`, which then prints the manifest and passes it to the process substitution. The `manifest` text should start after a newline after the `'MANIFEST_EOF'` part. You can put anything as `manifest` text other than `MANIFEST_EOF` which when read, ends the `manifest`. The ending `MANIFEST_EOF` should be alone on a separate line. The starting `'MANIFEST_EOF'` is surrounded with single quotes so that the `manifest` is considered a literal string and variable expansion, etc doesn't happen. You can remove those if you want expansion to happen.

```shell
cat <<'MANIFEST_EOF'

MANIFEST_EOF
```

Basically any text you put inside the `cat` heredoc will be passed to the process substitution which will create a temporary file descriptor for it at `/proc/self/fd/<n>` where `<n>` is fd number and this path is then passed to `temporal-src-network` as an argument. The `temporal-src-network` scripts reads the `manifest` text from this fd. **Since the fd path will not have a file extension, it will be assumed to be in `yaml` format unless `--manifests-format` argument is passed with a different value.**

For example:

```shell
python3 ../src/__main__.py -vv --manifests-format=yaml setup <(cat <<'MANIFEST_EOF'
project:
  project_src_checkout:
    src_url: git@github.com:stargateoss/project.git
    git_auth_token_var: GITHUB_TOKEN
    sparse_checkout: |
      dir1/
      dir2/subdir1
    submodules: recursive
MANIFEST_EOF
)
```

You can also pass multiple manifests in the same manifest file or in same process substitution, check [Multiple Projects](config/index.md#multiple-projects) example.

For example:

```shell
python3 ../src/__main__.py -vv setup <(cat <<'MANIFEST_EOF'
project:
  project_root_dir: /path/to/project1
  project_src_checkout:
    src_url: git@github.com:stargateoss/project1.git
    git_auth_token_var: GIT_AUTH_TOKEN

...
---

project:
  project_root_dir: /path/to/project2
  project_src_checkout:
    src_url: git@github.com:stargateoss/project2.git
    git_auth_token_var: GIT_AUTH_TOKEN
MANIFEST_EOF
)
```

---

&nbsp;





## Command Types

The following command types are supported.

&nbsp;

### Setup

The `setup` command set ups the project and its modules in the following sequence.

- Setup project.
  - Delete [`project.project_root_dir`](config/project.md#projectrootdir) if [`project.remove_project_root_dir_for_commands`](config/project.md#removeprojectrootdirforcommands) contains `setup` (By default it does not).
  - Checkout the project if [`project.project_src_checkout`](config/project.md#project_src_checkout) is set.
  - Create the project symlinks if [`project.project_symlinks.list`](config/symlinks.md#list) is set under [`project.project_symlinks`](config/project.md#project_symlinks).
- For all `modules` in [`project.modules.list`](config/modules.md#list) if [`project.modules`](config/project.md#modules) is set.
  - For all `versions` in [`project.modules.list.<module_name>.versions.list`](config/versions.md#list) under [`project.modules.list.<module_name>.versions`](config/module.md#versions).
    - Delete `version_root_dir` if [`version.remove_version_root_dir_for_commands`](config/version.md#removeversionrootdirforcommands) contains `setup` (By default it does).
    - Checkout the version as per [`version.version_src_checkout`](config/version.md#versionsrccheckout).
    - Create the version symlinks if [`version.version_symlinks.list`](config/symlinks.md#list) is set under [`version.version_symlinks`](config/version.md#versionsymlinks).

### Remove

The `remove` command removes the project and its modules in the following sequence.

- For all `modules` in [`project.modules.list`](config/modules.md#list) if [`project.modules`](config/project.md#modules) is set.
  - For all `versions` in [`project.modules.list.<module_name>.versions.list`](config/versions.md#list) under [`project.modules.list.<module_name>.versions`](config/module.md#versions).
    - Delete the version symlinks if [`version.version_symlinks.list`](config/symlinks.md#list) is set under [`version.version_symlinks`](config/version.md#versionsymlinks).
    - Delete `version_root_dir` if [`version.remove_version_root_dir_for_commands`](config/version.md#removeversionrootdirforcommands) contains `remove` (By default it does).
  - Delete [`module.module_root_dir`](config/module.md#modulerootdir) if [`module.remove_module_root_dir_for_commands`](config/module.md#removemodulerootdirforcommands) contains `remove` (By default it does).
- Remove project.
  - Delete the project symlinks if [`project.project_symlinks.list`](config/symlinks.md#list) is set under [`project.project_symlinks`](config/project.md#project_symlinks).
  - Delete [`project.project_root_dir`](config/project.md#projectrootdir) if [`project.remove_project_root_dir_for_commands`](config/project.md#removeprojectrootdirforcommands) contains `remove` (By default it does not).

---

&nbsp;





[`config`]: config/index.md
