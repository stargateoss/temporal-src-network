# Version Config

The version config is defined in the `project.modules.list.<module_name>.versions.list` `dict` key. It contains config of a project module `version`.

See also [`Supported Levels and Modes`](index.md#supported-levels-and-modes) for more info on **Supported Levels** and **Level Mode** info of keys.

### Contents

- [Keys](#keys)
    - [`ignore`](#ignore)
    - [`remove_version_root_dir_for_commands`](#removeversionrootdirforcommands)
    - [`version_src_checkout`](#versionsrccheckout)
    - [`version_symlinks`](#versionsymlinks)

---

&nbsp;





## Keys

The following keys are supported.

&nbsp;

### ignore

Whether to ignore processing of this module version for `temporal-src-network` commands.

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `false`

**Values:**

- `true` - Ignore processing this version.

- `false` - Do not ignore processing this version.

**Examples:**

```yaml
project:
  modules:
    list:
      foo:
        versions:
          list:
            latest:
              # Ignore this version
              ignore: true
```

## &nbsp;



### remove_version_root_dir_for_commands

The [command types] for which to remove the `version_root_dir`.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `setup,remove`

**Supported Levels**: (`module`, `version`)

**Values:**

A comma separated list of [command types].

- `setup` - The `version_root_dir` will be removed before setup of [`version_src_checkout`](#versionsrccheckout) and [`version_symlinks`](#versionsymlinks).

- `remove` - The `version_root_dir` will be removed after removal of [`version_symlinks`](#versionsymlinks) and before removal of its [`module`](#module) as per [`module.remove_module_root_dir_for_commands`](module.md#removemodulerootdirforcommands).

Since [`module.module_root_dir`](module.md#modulerootdir) is the same as `version_root_dir` if [`single_version`](versions.md#singleversion) is `true` or otherwise is the parent directory of `version_root_dir`, so to disable removal you need to remove required command from `remove_module_root_dir_for_commands` as well if it engages for that command, like for `remove` command.

**Examples:**

```yaml
project:
  modules:
    list:
      foo:
        # Do not remove module_root_dir and version_root_dir for any command
        remove_module_root_dir_for_commands: null
        remove_version_root_dir_for_commands: null
        versions:
          single_version: true|false
          list:
            latest:
              ...

      bar:
        # Remove module_root_dir and version_root_dir only for setup command
        remove_module_root_dir_for_commands: null
        remove_version_root_dir_for_commands: setup
        versions:
          single_version: true
          list:
            latest:
              ...

      baz:
        # Remove version_root_dir only for remove command without removing module_root_dir
        # The version_root_dir will not be removed for setup command
        remove_module_root_dir_for_commands: null
        remove_version_root_dir_for_commands: remove
        versions:
          single_version: false
          list:
            latest:
              ...

      qux:
        # Remove version_root_dir only for setup command
        remove_module_root_dir_for_commands: null
        remove_version_root_dir_for_commands: setup
        versions:
          single_version: false
          list:
            latest:
              ...
```

## &nbsp;



### version_src_checkout

The config required to checkout the source of a `version` of the `module`.

Check [`src_checkout`](src-checkout.md) docs for supported keys. Only the keys that have the value `version` in their `Supported Levels` will be used.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

## &nbsp;



### version_symlinks

The config required to manage symlinks for the `version` of the `module`.

Check [`symlinks`](symlinks.md) docs for supported keys.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

---

&nbsp;





[command types]: ../index.md#command-types

[`>= 0.1.0`]: https://github.com/stargateoss/temporal-src-network/releases/tag/v0.1.0
