# Modules Config

The `modules` config is defined in the `project.modules` `dict` key. It contains shared config of project `modules` and `versions`.

### Contents

- [Keys](#keys)
    - [`list`](#list)
    - [`version_src_checkout`](#versionsrccheckout)

---

&nbsp;





## Keys

The following keys are supported.

&nbsp;

### list

The list of [module configs](#module-config) of the project.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

**Values:**

A `dict` where each `dict` subkey is a separate [module config](#module-config). The key names of `dict` subkeys are the `module_name` for the modules.

**Examples:**

```yaml
project:
  modules:
    list:
      foo:
        ...
      bar:
        ...
```

## &nbsp;



### version_src_checkout

The config required to checkout the source of a `version` of a `module`.

Check [`src_checkout`](src-checkout.md) docs for supported keys. Only the keys that have the value `modules` in their `Supported Levels` will be used.

**Type:** `dict`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `null`

---

&nbsp;





[`>= 0.1.0`]: https://github.com/stargateoss/temporal-src-network/releases/tag/v0.1.0
