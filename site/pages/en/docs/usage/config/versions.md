# Versions Config

The `versions` config is defined in the `project.modules.list.<module_name>.versions` `dict` key. It contains shared config of project module `versions`.

### Contents

- [Keys](#keys)
    - [`single_version`](#singleversion)
    - [`list`](#list)

---

&nbsp;





## Keys

The following keys are supported.

&nbsp;

### single_version

Whether the module contains a single version or multiple versions.

**The value set decides the `version_root_dir` path.**
- If `true`, then only `1` [version config](#version-config) must be defined the the [`list`](#list) value. If `>= 1` [version configs](#version-config) are defined, only the first one will be used and a warning will be logged. The `version_root_dir` will be the same as the expanded [`module.module_root_dir`](module.md#modulerootdir) path.
- If `false`, then `>= 1` [version configs](#version-config) must be defined the the [`list`](#list) value. The `version_root_dir` will be set to the [`version_name`](#list) directory under the expanded [`module.module_root_dir`](module.md#modulerootdir) path.

A dedicated key is needed for this because initially only `1` version may be defined for a module, with plans for more versions to be added in future, and a dedicated `version_name` directory under `module_root_dir` must still be used for `version_root_dir` for that initial `1` version, instead of it being the same as `module_root_dir`.

The `version_root_dir` will be deleted and so it must be under the [`project.project_root_dir`](project.md#projectrootdir) for `single_version`, otherwise under [`module.module_root_dir`](module.md#modulerootdir) so that important directories outside them are not accidentally deleted, especially if `project_root_dir` is set to the filesystem root `/`.

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `true`

**Values:**

- `true` - If module is supposed to only contain `1` version.

- `false` - If module is supposed to contain `>= 1` versions.

**Examples:**

```yaml
project:
  project_root_dir: /path/to/project
  modules:
    list:
      foo:
        # Expands to `/path/to/project/_modules/foo`
        module_root_dir: _modules/foo
        versions:
          single_version: true
          list:
            latest:
              # `version_root_dir` will be set to `/path/to/project/_modules/foo`
              ...
      bar:
        # Expands to `/path/to/project/_modules/bar`
        module_root_dir: _modules/bar
        versions:
          single_version: false
          list:
            latest:
              # `version_root_dir` will be set to `/path/to/project/_modules/bar/latest`
              ...
      baz:
        # Expands to `/path/to/project/_modules/baz`
        module_root_dir: _modules/baz
        versions:
          single_version: false
          list:
            latest:
              # `version_root_dir` will be set to `/path/to/project/_modules/baz/latest`
              ...
            stable:
              # `version_root_dir` will be set to `/path/to/project/_modules/baz/stable`
              ...
```

## &nbsp;



### list

The list of [version configs](#version-config) of the module.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

**Values:**

A `dict` where each `dict` subkey is a separate [version config](#version-config). The key names of `dict` subkeys are the `version_name` for the versions and they must not contain the platform path separator (`/` or `\`) or `null` bytes or equal `.` or `..`.

**Examples:**

```yaml
project:
  modules:
    list:
      foo:
        versions:
          list:
            latest:
              ...
            stable:
              ...
```

---

&nbsp;





[`>= 0.1.0`]: https://github.com/stargateoss/temporal-src-network/releases/tag/v0.1.0
