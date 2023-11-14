# temporal-src-network

The `temporal-src-network` is `python3` utility to build temporal sources network.

### Contents

- [Docs](#docs)
- [Planned Work](#planned-work)
- [License](#license)
- [Credits](#credits)
- [See Also](#see-also)

---

&nbsp;





## Docs

Check docs [here](site/pages/en/docs/index.md).

---

&nbsp;





## Planned Work

- Source checkout
    - `git`
        - Implement the `TODO` items in [`git_src_provider.py`](src/temporal_src_network/src_checkout/git/git_src_provider.py) and [`git_auth_manager.py`](src/temporal_src_network/src_checkout/git/git_auth_manager.py) to be consistent with [`actions/checkout`].
        -  Custom `ssh` key support for `ssh` urls checkouts. ([1](https://github.com/actions/checkout/blob/a12a3943b4bdde767164f792f33f40b04645d846/src/git-auth-helper.ts#L190))
    - Checking out `zip`, `tar` and `raw` files.
- Custom shell command executions for different events where a list of events to execute is provided in the `events` sub key for `project.project_commands`, `module.module_commands` and `version.version_commands` keys.
    - For each key, events like `setup__enter`, `setup__pre_checkout`, `setup__post_checkout`, `setup__pre_create_symlinks`, `setup__post_create_symlinks`, `setup__exit` would be supported for `setup` commands and `remove__enter`, `remove__pre_delete_symlinks`, `remove__post_delete_symlinks`, `remove__exit` would be supported for `remove` commands, etc.
    - `${{ tsn.var }}` placeholder expansions would be done before execution.

---

&nbsp;





## License

Check license info [here](LICENSE.md).

---

&nbsp;





## Credits

- [`actions/checkout`] for `git` repositories checkout reference code.

---

&nbsp;





## See also

- [`stargateoss/temporal-src-network-action`](https://github.com/stargateoss/temporal-src-network-action).

---

&nbsp;





[`actions/checkout`]: https://github.com/actions/checkout
