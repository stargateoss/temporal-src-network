# Symlink Config

The symlink config is defined in the `project.project_symlinks.list` key for `project` symlinks and in the `project.modules.list.<module_name>.symlinks.list` and `project.modules.list.<module_name>.versions.<version_name>.symlinks.list` `dict` keys for `version` symlinks.

### Contents

- [Keys](#keys)
    - [`ignore`](#ignore)
    - [`target`](#target)
    - [`dest`](#dest)
    - [`target_expansions`](#targetexpansions)
    - [`dest_expansions`](#destexpansions)
    - [`target_is_directory`](#targetisdirectory)
    - [`target_no_exist_mode`](#targetnoexistmode)
    - [`dest_already_exists_mode`](#destalreadyexistsmode)
- [Placeholder Expansion](#placeholder-expansions)

---

&nbsp;





## Keys

The following keys are supported.

&nbsp;

### ignore

Whether to ignore processing of this symlink for `temporal-src-network` commands.

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `false`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `true` - Ignore processing this symlink.

- `false` - Do not ignore processing this symlink.

**Examples:**

```yaml
project:
  modules:
    list:
      foo:
        version_symlinks:
          list:
            sym1:
              # Ignore this symlink
              ignore: true
```

## &nbsp;



### target

The symlink target path at which the symlink file should point to.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

**Related keys:** [`target_expansions`](#targetexpansions), [`target_is_directory`](#targetisdirectory), [`target_no_exist_mode`](#targetnoexistmode)

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

`path/to/target` - The absolute or relative path to symlink target.

[`Environmental Variable Expansions`] and then [`Placeholder Expansions`] will be done on the path set.

**Examples:**

```yaml
project:
  project_root_dir: /path/to/project
  project_symlinks:
    list:
      file1:
        # Expands to `/path/to/project/file1`
        target: "@PROJECT__ROOT_DIR@/file1"

        # Expands to `/path/to/config/file1` if `$CONFIG_DIR` env variable is exported to `/path/to/config`
        target: $CONFIG_DIR/file1

  modules:
    list:
      foo:
        module_root_dir: _modules/foo
        versions:
          # single_version: true
          list:
            stable:
              version_symlinks:
                list:
                  dir1:
                    # Expands to `../../../_modules/foo/dir1`
                    target: ../../../@VERSION__ROOT_SUB_DIR@/dir1

                    # Expands to `/path/to/project/_modules/foo/dir1`
                    target: "@VERSION__ROOT_DIR@/dir1"
```

## &nbsp;



### dest

The symlink destination path at which to create the symlink file.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

**Related keys:** [`dest_expansions`](#destexpansions), [`dest_already_exists_mode`](#destalreadyexistsmode)

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

`path/to/target` - The absolute or relative path to symlink destination. If path is relative, then it will automatically be prefixed with [`project.project_root_dir`](project.md#projectrootdir).

[`Environmental Variable Expansions`] and then [`Placeholder Expansions`] will be done on the path set.

**Examples:**

```yaml
project:
  project_root_dir: $PROJECT_DIR # env variable exported to `/path/to/project`
  project_symlinks:
    list:
      file1:
        # Expands to `/path/to/project/sym1`
        dest: "@PROJECT__ROOT_DIR@/sym1"

        # Expands to `/path/to/project/sym1`
        dest: $PROJECT_DIR/sym1

  modules:
    list:
      foo:
        module_root_dir: _modules/foo
        versions:
          # single_version: true
          list:
            stable:
              version_symlinks:
                list:
                  dir1:
                    # Expands to `/path/to/project/a/b/foo/stable`
                    dest: a/b/foo/@VERSION__NAME@

                    # Expands to `/path/to/project/a/b/foo/stable`
                    dest: $PROJECT_DIR/a/b/foo/@VERSION__NAME@
```

## &nbsp;



### target_expansions

The expansions that should done for the [`target`](#target) value.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `env,placeholder`

**Related keys:** [`target`](#target)

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

A comma separated list of expansion types. If set to `null` or empty string, then no expansions will be done.

- `env` - Do [`Environmental Variable Expansions`].

- `placeholder` - Do [`Placeholder Expansions`].

**Examples:**

```yaml
file1:
  # Only do environmental variable expansions
  target_expansions: "env"

  # Only do placeholder expansions
  target_expansions: "placeholder"

  # Do no expansion
  target_expansions: "placeholder"
```

## &nbsp;



### dest_expansions

The expansions that should done for the [`dest`](#dest) value.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `env,placeholder`

**Related keys:** [`dest`](#dest)

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

A comma separated list of expansion types. If set to `null` or empty string, then no expansions will be done.

- `env` - Do [`Environmental Variable Expansions`].

- `placeholder` - Do [`Placeholder Expansions`].

**Examples:**

```yaml
file1:
  # Only do environmental variable expansions
  dest_expansions: "env"

  # Only do placeholder expansions
  dest_expansions: "placeholder"

  # Do no expansion
  dest_expansions: "placeholder"
```

## &nbsp;



### target_is_directory

The `target_is_directory` argument value to pass to [`os.symlink()`](https://docs.python.org/3/library/os.html#os.symlink) so that symlink to [`target`](#target) is created as a directory.

On Windows, a symlink represents either a file or a directory, and does not morph to the target dynamically. If the target is present, the type of the symlink will be created to match. Otherwise, the symlink will be created as a directory if `target_is_directory` is `true` (the default) or a file symlink otherwise. **On non-Windows platforms, `target_is_directory` is ignored.**

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `true`

**Related keys:** [`target`](#target)

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `true` - Is a symlink to a directory.

- `false` - Is a symlink to a file.

**Examples:**

```yaml
file1:
  # Create a file symlink on Windows
  target_is_directory: false
```

## &nbsp;



### target_no_exist_mode

The mode for what to do if symlink [`target`](#target) does not exist.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `disallow`

**Related keys:** [`target`](#target)

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

The value for mode.

- `ignore` - Ignore creating the symlink and do not exit with error.

- `allow` - Create the (dangling) symlink.

- `disallow` - Exit with error.

The `ignore` value may be useful if a specific module `version` does not have the symlink `target` and symlinks are defined at the `module` level to be created for all versions.

**Examples:**

```yaml
file1:
  # Do not create this symlink if target does not exist
  target_no_exist_mode: "ignore"
```

## &nbsp;



### dest_already_exists_mode

The mode for what to do if symlink [`dest`](#dest) already exists.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `overwrite_only_if_symlink`

**Related keys:** [`dest`](#dest)

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

The value for mode.

- `ignore` - Ignore creating the symlink.

- `overwrite` - Delete any existing file at destination path regardless of its file type and then create the symlink at the destination path.

- `overwrite_only_if_symlink` - Delete any existing file at destination path but only if it is a `symlink` file and then create the symlink at the destination path.

- `disallow` - Exit with error.

**Examples:**

```yaml
file1:
  # Overwrite destination file regardless of its file type
  dest_already_exists_mode: "overwrite"
```

---

&nbsp;





## Placeholder Expansions

For the [`target`](#target) and [`dest`](#dest) keys, the following placeholders in the values in the format `@NAME@` will be expanded. Placeholder expansions are done **after** [`Environmental Variable Expansions`].

**If the key value starts with the at sign character `@`, like for a placeholder, then surround value with double quotes `"` in `yaml` manifest, otherwise the `while scanning for the next token
found character '@' that cannot start any token` error will be generated.**

For [`project.project_symlinks`](project.md#projectsymlinks) and [`version.version_symlinks`](version.md#versionsymlinks):

 - `PROJECT__ROOT_DIR`: The [`project.project_root_dir`](project.md#projectrootdir).

 For [`version.version_symlinks`](version.md#versionsymlinks):

 - `MODULE__NAME`: The `module_name` defined in [`project.modules.list`](modules.md#list).
 - `MODULE__ROOT_SUB_DIR`: The [`module.module_root_dir`](module.md#modulerootdir) relative to [`project.project_root_dir`](project.md#projectrootdir).
 - `MODULE__ROOT_DIR`: The [`module.module_root_dir`](module.md#modulerootdir).

 - `VERSION__NAME`: The `version_name` defined in [`project.modules.list`](versions.md#list).
 - `VERSION__ROOT_SUB_DIR`: The [`version.version_root_dir`](module.md#modulerootdir) relative to [`project.project_root_dir`](project.md#projectrootdir).
 - `VERSION__ROOT_DIR`: The `version.version_root_dir`.

## &nbsp;

&nbsp;





[`Environmental Variable Expansions`]: index.md#environmental-variable-expansions
[`Placeholder Expansions`]: #placeholder-expansions

[`>= 0.1.0`]: https://github.com/stargateoss/temporal-src-network/releases/tag/v0.1.0
