# Symlinks Config

The `symlinks` config is defined in the `project.project_symlinks` `dict` key for managing symlinks of the `project` and in the `project.modules.list.<module_name>.version_symlinks` and `project.modules.list.<module_name>.versions.<version_name>.version_symlinks` `dict` keys for managing symlinks of a `version`. It contains the config for what symlinks to create for `temporal-src-network` `setup` commands after the [checkout](#sparse-checkout.md) step, and what symlinks to `remove` for `temporal-src-network` `remove` commands. The symlinks can be made at the paths under the project root directory, like to the module `version` files/directories checked out that may be required to build the project.

See also [`Supported Levels and Modes`](index.md#supported-levels-and-modes) for more info on **Supported Levels** and **Level Mode** info of keys.

### Contents

- [Keys](#keys)
    - [`symlinks_list_level_mode`](#symlinkslistlevelmode)
    - [`list`](#list)

---

&nbsp;





## Keys

The following keys are supported.

&nbsp;

### symlinks_list_level_mode

The [`Levels Mode`] mode for the [`list`](#list) key.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `add`

**Related keys:** [`list`](#list)

**Supported Levels**: `version`

**Values:**

- `add` - The value of [`list`](#list) at `version` level will be added to any value at `module` level.

- `override` - The value of [`list`](#list) at `version` level will override any value at `module` level.

**Examples:**

```yaml
project:
  modules:
    list:
      foo:
        version_symlinks:
          list:
            dir1
              ...
        versions:
          list:
            latest:
              version_symlinks:
                symlinks_list_level_mode: override
                list:
                  # Only create `dir2` symlink and not the module level `dir1` symlink
                  dir2:
                    ...
```

## &nbsp;



### list

The list of [symlink configs](#symlink-config) of the module or version.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

**Related keys:** [`symlinks_list_level_mode`](#symlinkslistlevelmode)

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

A `dict` where each `dict` subkey is a separate [symlink config](#symlink-config). The key names of `dict` subkeys are the `symlink_name` for the symlinks.

**Examples:**

```yaml
project:
  project_symlinks:
    list:
      sym1:
        ...

  modules:
    list:
      foo:
        version_symlinks:
          list:
            sym1:
              ...
            sym2:
              ...
        versions:
          list:
            latest:
              version_symlinks:
                list:
                  sym3:
                    ...
```

---

&nbsp;





[`Levels Mode`]: index.md#supported-levels-and-modes

[`>= 0.1.0`]: https://github.com/stargateoss/temporal-src-network/releases/tag/v0.1.0
