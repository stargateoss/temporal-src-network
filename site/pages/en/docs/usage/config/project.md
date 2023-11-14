# Project Config

The `project` config is defined in the top level `project` `dict` key. It contains host project config and shared config of project `modules` and `versions`.

### Contents

- [Keys](#keys)
    - [`project_root_dir`](#projectrootdir)
    - [`remove_project_root_dir_for_commands`](#removeprojectrootdirforcommands)
    - [`project_src_checkout`](#projectsrccheckout)
    - [`project_symlinks`](#projectsymlinks)
    - [`modules`](#modules)

---

&nbsp;





## Keys

The following keys are supported.

&nbsp;

### project_root_dir

Path to root directory of host project under which the sources network needs to be built containing `modules` and their `versions`.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:**

Precedence is in following order.

- `project_root_dir` if set.

- [`$GITHUB_WORKSPACE`] environmental variable value if `$GITHUB_ACTIONS` equals `true` to signify running in a GitHub actions workflow.

- [Current working directory (`cwd`)].

**Related keys:** [`remove_project_root_dir_for_commands`](#removeprojectrootdirforcommands)

**Values:**

`/path/to/directory` - The relative or absolute path to the project root directory.

[`Environmental Variable Expansions`](index.md#environmental-variable-expansions) will be done on the path set.

The [`$GITHUB_WORKSPACE`] environmental variable for GitHub actions workflow is the default working directory on the runner for steps, and the default location of the repository when using the [`actions/checkout`] action. For example, `/home/runner/work/my-repo-name/my-repo-name`. If you set `project_root_dir` to a custom environmental variable like `$PROJECT_ROOT_DIR` and are running in a GitHub actions workflow, then export it with the [`env` key](https://docs.github.com/en/actions/learn-github-actions/variables#defining-environment-variables-for-a-single-workflow) of the action and set its value to [`github.workspace`](https://docs.github.com/en/actions/learn-github-actions/contexts#github-context), same as [`$GITHUB_WORKSPACE`].

```yaml
steps:
  - name: Checkout repository
  env:
    PROJECT_ROOT_DIR: ${{ github.workspace }}
```

**Examples:**

```yaml
project:
  # Relative path to current working directory
  project_root_dir: path/to/project

  # Absolute path
  project_root_dir: /path/to/project

  # Environmental variable
  project_root_dir: $PROJECT_ROOT_DIR
```

## &nbsp;



### remove_project_root_dir_for_commands

The [command types] for which to remove the [`project_root_dir`](#projectrootdir).

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

**Related keys:** [`project_root_dir`](#projectrootdir)

**Values:**

A comma separated list of [command types].

- `setup` - The `project_root_dir` will be removed at the start of the command before setup of [`project_src_checkout`](#projectsrccheckout) and [`project_symlinks`](#projectsymlinks) and the setup of any [`modules`](#modules).

- `remove` - The `project_root_dir` will be removed at the end of the command after removal of any [`modules`](#modules) and [`project_symlinks`](#projectsymlinks).

**Examples:**

```yaml
project:
  # Remove project_root_dir for setup and remove commands
  remove_project_root_dir_for_commands: setup,remove

  # Remove project_root_dir only for setup command
  remove_project_root_dir_for_commands: setup
```

## &nbsp;



### project_src_checkout

The config required to checkout the source of the `project`.

Check [`src_checkout`](src-checkout.md) docs for supported keys. Only the keys that have the value `project` in their `Supported Levels` will be used.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

## &nbsp;



### project_symlinks

The config required to manage symlinks for the `project`.

Check [`symlinks`](symlinks.md) docs for supported keys.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

## &nbsp;

&nbsp;



### modules

The `dict` for the [modules configs](modules.md).

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

---

&nbsp;





[`actions/checkout`]: https://github.com/actions/checkout
[command types]: ../index.md#command-types
[Current working directory (`cwd`)]: https://www.gnu.org/software/libc/manual/html_node/Working-Directory.html
[`$GITHUB_WORKSPACE`]: https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables

[`>= 0.1.0`]: https://github.com/stargateoss/temporal-src-network/releases/tag/v0.1.0
