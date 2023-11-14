# Module Config

The module config is defined in the `project.modules.list.<module_name>` `dict` key. It contains config of a project `module` and its `versions`.

### Contents

- [Keys](#keys)
    - [`ignore`](#ignore)
    - [`module_root_dir`](#modulerootdir)
    - [`remove_module_root_dir_for_commands`](#removemodulerootdirforcommands)
    - [`version_src_checkout`](#versionsrccheckout)
    - [`version_symlinks`](#versionsymlinks)
    - [`versions`](#versions)

---

&nbsp;





## Keys

The following keys are supported.

&nbsp;

### ignore

Whether to ignore processing of this module for `temporal-src-network` commands.

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `false`

**Values:**

- `true` - Ignore processing this module.

- `false` - Do not ignore processing this module.

**Examples:**

```yaml
project:
  modules:
    list:
      foo:
        # Ignore this module
        ignore: true
```

## &nbsp;



### module_root_dir

Sub directory path to root directory of the module under which the sources network needs to be built containing the `module` and its `versions`.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

**Related keys:** [`remove_module_root_dir_for_commands`](#removemodulerootdirforcommands)

**Values:**

`path/to/directory` - The absolute or relative sub directory path under the [`project.project_root_dir`](project.md#projectrootdir).

[`Environmental Variable Expansions`](index.md#environmental-variable-expansions) will be done on the path set.

The `module_root_dir` will be deleted and so it must be under the `project_root_dir` so that important directories outside it are not accidentally deleted, especially if `project_root_dir` is set to the filesystem root `/`.

**Examples:**

```yaml
project:
  project_root_dir: /path/to/project
  modules:
    list:
      foo:
        # Expands to `/path/to/project/_modules/foo`
        module_root_dir: _modules/foo
```

## &nbsp;



### remove_module_root_dir_for_commands

The [command types] for which to remove the [`module_root_dir`](#modulerootdir).

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `remove`

**Related keys:** [`module_root_dir`](#modulerootdir)

**Values:**

A comma separated list of [command types].

- `remove` - The `module_root_dir` will be removed after removal of all its [`versions`](#versions) as per [`version.remove_version_root_dir_for_commands`](version.md#removeversionrootdirforcommands).

Since `module_root_dir` and `version_root_dir` are the same if [`single_version`](versions.md#singleversion) is `true`, so to disable removal you need to remove required command from `remove_version_root_dir_for_commands` as well if it engages for the command, like for `remove` command.

**Examples:**

Check examples for [`version.remove_version_root_dir_for_commands`](version.md#removeversionrootdirforcommands).

## &nbsp;



### version_src_checkout

The config required to checkout the source of a `version` of the `module`.

Check [`src_checkout`](src-checkout.md) docs for supported keys. Only the keys that have the value `module` in their `Supported Levels` will be used.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

## &nbsp;



### version_symlinks

The config required to manage symlinks for all `versions` of the `module`.

Check [`symlinks`](symlinks.md) docs for supported keys.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

## &nbsp;



### versions

The `dict` for the [versions configs](versions.md).

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

---

&nbsp;





[command types]: ../index.md#command-types

[`>= 0.1.0`]: https://github.com/stargateoss/temporal-src-network/releases/tag/v0.1.0
