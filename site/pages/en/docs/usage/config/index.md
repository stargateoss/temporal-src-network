# Config

The `manifest` files passed to `temporal-src-network` contain the `config` on how to build the sources network. Its design is a bit complex to support ease of building multiple sources network with multiple versions per module.

- The top level `project` `dict` key defines the [`project` config](project.md).
- The [`project.modules`](project.md#modules) `dict` key defines the [`modules` config](modules.md) for all the modules.
- The [`project.modules.list`](modules.md#list) `dict` key defines the [`module` configs](module.md) where each `dict` subkey is a separate module.
- The [`project.modules.list.<module_name>.versions`](module.md#versions) `dict` key defines the [`versions` config](versions.md) for all versions of a module.
- The [`project.modules.list.<module_name>.versions.list`](versions.md#list) `dict` key defines the [`version` configs](version.md) for a module where each `dict` subkey is a separate version.
- Some sub keys exist at multiple levels and some sub keys will not exist at all levels. Check [`Supported Levels and Modes`](#supported-levels-and-modes) for more info.

### Contents

- [Example YAML Manifests](#example-yaml-manifests)
- [Supported Levels and Modes](#supported-levels-and-modes)
- [Environmental Variable Expansions](#environmental-variable-expansions)

---

&nbsp;





## Example YAML Manifests

Following are various examples manifests.

&nbsp;

### Basic Structure

```yml
project:
  ...
  project_src_checkout:
    ...
  project_symlinks:
    list:
      ...


  modules:
    version_src_checkout:
      ...
    list:
      module_1:
        ...
        versions:
          ...
          list:
            version_1:
              ...
              version_src_checkout:
                ...
              version_symlinks:
                ...

      module_2:
         ...
        version_src_checkout:
           ...
        version_symlinks:
          ...
          list:
            ...

        versions:
          single_version: false # **important**
          list:
            ...
            version_1:
              version_src_checkout:
                ...
              version_symlinks:
                ...
                list:
                  ...
            version_2:
              version_src_checkout:
                ...
              version_symlinks:
                ...
                list:
                  ...

            version_3:
              version_src_checkout:
                ...
              version_symlinks:
                ...
                list:
                  ...
```

## &nbsp;

&nbsp;



### Standalone Project

This can be used to just checkout a standalone project with no external [`modules`](modules.md), like [`actions/checkout`] does.

We use a `ssh` url for git `src_url` so that `ssh` authentication can be used for local checkouts and url can automatically be converted to a `https` url if `$GITHUB_TOKEN` environmental variable is set for token authentication, like by GitHub actions workflow if it is hosted in the same repository. Check [`src_checkout.src_url`](src_checkout.md#srcurl) and [`src_checkout.git_auth_token_var`](src-checkout.md#gitauthtokenvar) for more info.

The [`$GITHUB_WORKSPACE`] will be used as [`project.project_root_dir`] automatically if running in a GitHub actions workflow, otherwise the [Current working directory (`cwd`)].

##### `setup` command

- Setup project.  
    - Checkout default branch of a standalone project.  
        - Enable sparse checkout for `/dir1` and `/dir2/subdir1` directories.  
        - Recursively checkout any [`git` submodules].  

```yaml
project:
  project_src_checkout:
    src_url: git@github.com:stargateoss/project.git
    git_auth_token_var: GITHUB_TOKEN
    sparse_checkout: |
      dir1/
      dir2/subdir1
    submodules: recursive
```

## &nbsp;

&nbsp;



### Standalone Project (json)

The same as [Standalone Project Checkout](#standalone-project), except a json manifest instead of yaml. *One json example is enough!*

```json
{
  "project": {
    "project_src_checkout": {
      "src_url": "git@github.com:stargateoss/project.git",
      "git_auth_token_var": "GITHUB_TOKEN",
      "sparse_checkout": "/dir1/\n/dir2/subfile1",
      "submodules": "recursive"
    }
  }
}
```

## &nbsp;

&nbsp;



### Project With Single Module

This can be used to checkout a project that also depends on a single version of an external module/repository, like for a library that is a build dependency.

We use a `ssh` url for git `src_url` so that `ssh` authentication can be used for local checkouts and url can automatically be converted to a `https` url if custom `$GIT_AUTH_TOKEN` environmental variable is set for token authentication, like by GitHub actions workflow. We do not use `$GITHUB_TOKEN` as it will not have access to external repositories and it only has permissions to checkout the repository that hosts the workflow. Check [`src_checkout.src_url`](src_checkout.md#srcurl) and [`src_checkout.git_auth_token_var`](src-checkout.md#gitauthtokenvar) for more info.

The [`$GITHUB_WORKSPACE`] will be used as [`project.project_root_dir`] automatically if running in a GitHub actions workflow, otherwise the [Current working directory (`cwd`)].

##### `setup` command

- Setup project.  
    - Remove [`project.project_root_dir`] if it already exists.  
    - Checkout `master` branch of project.  
        - Recursively checkout any [`git` submodules].  
- Setup modules.  
    - Setup `foo` module.  
        - Setup `release` version.  
            - Checkout `v0.1.0` tag of the `foo` repository as an external [`module`](modules.md) at `_modules/foo` directory.  
                - Enable sparse checkout for `/lib` directory of `foo` module.  
            - Setup module symlinks.  
                - Create a symlink to `/lib` directory of `foo` module at `/src/lib/foo` directory of the project.  

##### `remove` command

- Remove modules.  
    - Remove `foo` module.  
        - Remove `release` version.  
            - Remove module symlinks.  
                -  Delete symlink at `/src/lib/foo` directory of the project.  
            - Delete `version_root_dir` at `_modules/foo` directory.  
        - Delete [`module.module_root_dir`](module.md#modulerootdir) at `_modules/foo` directory.  
- Remove project.  
    - Delete [`project.project_root_dir`].  

```yaml
project:
  remove_project_root_dir_for_commands: setup,remove
  project_src_checkout:
    src_url: git@github.com:stargateoss/project.git
    git_auth_token_var: GIT_AUTH_TOKEN
    ref: refs/heads/master
    submodules: recursive

  modules:
    list:
      foo:
        module_root_dir: _modules/foo
        versions:
          list:
            release:
              version_src_checkout:
                src_url: git@github.com:stargateoss/foo.git
                git_auth_token_var: GIT_AUTH_TOKEN
                ref: refs/tags/v0.1.0
                sparse_checkout: |
                  /lib
                sparse_checkout_cone_mode: false
              version_symlinks:
                list:
                  foo:
                    target: "@VERSION__ROOT_DIR@/lib"
                    dest: "@PROJECT__ROOT_DIR@/src/lib/foo"
```

## &nbsp;

&nbsp;



### Project With Multiple Modules

This can be used to checkout a single version of multiple external modules/repositories, like for libraries that are build dependencies. This assumes that the host project has already been checkout out and if already running inside it, for example, the manifest for external modules can be part of the host project and external dependencies can be checked out if needed with `temporal-src-network -vv setup _modules/manifest.yml`.

We use a `ssh` url for git `src_url` so that `ssh` authentication can be used for local checkouts and url can automatically be converted to a `https` url if custom `$GIT_AUTH_TOKEN` environmental variable is set for token authentication, like by GitHub actions workflow. We do not use `$GITHUB_TOKEN` as it will not have access to external repositories and it only has permissions to checkout the repository that hosts the workflow. Check [`src_checkout.src_url`](src_checkout.md#srcurl) and [`src_checkout.git_auth_token_var`](src-checkout.md#gitauthtokenvar) for more info.

The [`$GITHUB_WORKSPACE`] will be used as [`project.project_root_dir`] automatically if running in a GitHub actions workflow, otherwise the [Current working directory (`cwd`)].

##### `setup` command

- Setup modules.  
    - Setup `foo` module.  
        - Setup `release` version.  
            - Checkout `v0.1.0` tag of the `foo` repository as an external [`module`](modules.md) under `_modules/foo` directory.  
                - Enable sparse checkout for `/lib` directory.  
            - Setup module symlinks.  
                - Create a symlink to `/lib` directory of `foo` module at `/src/lib/foo` directory of the the project.  
    - Setup `bar` module.  
        - Setup `latest` version.  
            - Checkout `master` branch of the `bar` repository as an external [`module`](modules.md) directly at the `src/lib/bar` directory of the project without creating a symlink.  
                - Enable sparse checkout for `/lib` directory.  

##### `remove` command

- Remove modules.  
    - Remove `foo` module.  
        - Remove `release` version.  
            - Remove module symlinks.  
                -  Delete symlink at `/src/lib/foo` directory of the project.  
            - Delete `version_root_dir` at `_modules/foo` directory.  
        - Delete [`module.module_root_dir`](module.md#modulerootdir) at `_modules/foo` directory.    
    - Remove `bar` module.  
        - Remove `latest` version.  
            - Delete `version_root_dir` at `src/lib/bar` directory.  
        - Delete [`module.module_root_dir`](module.md#modulerootdir) at `src/lib/bar` directory.  

```yaml
project:

  modules:
    version_src_checkout:
      git_auth_token_var: GIT_AUTH_TOKEN
    list:
      foo:
        module_root_dir: _modules/foo
        versions:
          list:
            release:
              version_src_checkout:
                src_url: git@github.com:stargateoss/foo.git
                ref: refs/tags/v0.1.0
                sparse_checkout: |
                  /lib
                sparse_checkout_cone_mode: false
              version_symlinks:
                list:
                  foo:
                    target: "@VERSION__ROOT_DIR@/lib"
                    dest: "@PROJECT__ROOT_DIR@/src/lib/foo"

      bar:
        module_root_dir: src/lib/bar
        versions:
          list:
            latest:
              version_src_checkout:
                src_url: git@github.com:stargateoss/bar.git
                ref: refs/heads/master
                sparse_checkout: |
                  /lib
                sparse_checkout_cone_mode: false
```

## &nbsp;

&nbsp;



### Project With Multiple Modules And Multiple Versions

This can be used to checkout multiple versions of multiple external modules/repositories, like for libraries that are build dependencies. The `project.project_src_checkout` dict can optionally be removed if the host project has already been checkout out and if already running inside it, for example, the manifest for external modules/versions can be part of the host project and external dependencies can be checked out if needed with `temporal-src-network -vv setup _modules/manifest.yml`.

We use a `ssh` url for git `src_url` so that `ssh` authentication can be used for local checkouts and url can automatically be converted to a `https` url if custom `$GIT_AUTH_TOKEN` environmental variable is set for token authentication, like by GitHub actions workflow. We do not use `$GITHUB_TOKEN` as it will not have access to external repositories and it only has permissions to checkout the repository that hosts the workflow. Check [`src_checkout.src_url`](src_checkout.md#srcurl) and [`src_checkout.git_auth_token_var`](src-checkout.md#gitauthtokenvar) for more info.

The [`$GITHUB_WORKSPACE`] will be used as [`project.project_root_dir`] automatically if running in a GitHub actions workflow, otherwise the [Current working directory (`cwd`)].

The following manifest lists all the possible keys that can exist at each level. The keys that are commented can be uncommented as needed and are just examples. Some keys have their values separated with `|` to list all the possible values.

##### `setup` command

- Setup project.  
    - Checkout `master` branch of project.  
        - Recursively checkout any [`git` submodules].  
    - Setup project symlinks.  
        - Create `root` symlink to [`project.project_root_dir`] at `/dir1/root` of the project.  
- Setup modules.  
    - Setup `foo` module.  
        - Setup `release` version.  
            - Checkout `master` branch of the `foo` repository as an external [`module`](modules.md) at `_modules/foo` directory.  
                - Enable sparse checkout for `/dir1` and `/dir2/subdir1` directories.  
            - Setup module symlinks.  
                - Create `dir1` symlink to `../../_modules/foo/dir1` at `/dir1/foo/stable` directory of the the project.  
    - Setup `bar` module.  
        - Setup `latest` version.  
            - Checkout `master` branch of the `bar` repository as an external [`module`](modules.md) at `_modules/bar/latest` directory.  
                 - Enable sparse checkout without cone mode for `/dir1/subdir1/*` pattern and `/dir2/subfile1` file and `/dir3/*` pattern.  
            - Setup module symlinks.  
                - Create `dir1/subdir1` symlink to `../../../_modules/bar/dir1/subdir1` at `/dir1/subdir1/bar/latest` directory of the the project if target exists.  
                - Create `dir2/subfile1` symlink to `../../_modules/bar/dir2/subfile1` at `/dir2/bar/latest` file of the the project if target exists.  
                - Create `dir3` symlink to `../../_modules/bar/dir3` at `/dir3/bar/latest` directory of the the project due to `sparse_checkout_level_mode=add` and overwrite any destination file that exists.  
        - Setup `stable` version.  
            - Checkout `v0.1.0` tag of the `bar` repository as an external [`module`](modules.md) at `_modules/bar/stable` directory.  
                - Enable sparse checkout without cone mode for `/dir1/subdir1/*` pattern and `/dir2/subfile1` file.  
            - Setup module symlinks.  
                - Create `dir1/subdir1` symlink to `../../../_modules/bar/dir1/subdir1` at `/dir1/subdir1/bar/stable` directory of the the project if target exists.  
                - Create `dir2/subfile1` symlink to `../../_modules/bar/dir2/subfile1` at `/dir2/bar/stable` file of the the project if target exists.  
        - Setup `v0.1.0` version.  
            - Checkout `v0.1.0` tag of the `bar` repository as an external [`module`](modules.md) at `_modules/bar/v0.1.0` directory.  
              - Enable sparse checkout without cone mode for `/dir1/subdir1/*` pattern and `/dir2/subfile1` file.  
            - Setup module symlinks.  
                - Create `dir1/subdir1` symlink to `../../../_modules/bar/dir1/subdir1` at `/dir1/subdir1/bar/v0.1.0` directory of the the project if target exists.  
                - Create `dir2/subfile1` symlink to `../../_modules/bar/dir2/subfile1` at `/dir2/bar/v0.1.0` file of the the project if target exists.  
        - Setup `legacy` version.  
            - Checkout `master` branch of the `bar-legacy` repository as an external [`module`](modules.md) at `_modules/bar/legacy` directory.  
                - Enable sparse checkout without cone mode for `/legacy-dir1/subdir1/*` pattern and `/legacy-dir2/subfile1` file.  
            - Setup module symlinks.  
                - Create `legacy-dir1/subdir1` symlink to `../../../_modules/bar/legacy-dir1/subdir1` at `/dir1/subdir1/bar/legacy` directory of the the project if target exists.  
                - Create `legacy-dir2/subfile1` symlink to `../../_modules/bar/legacy-dir2/subfile1` at `/dir2/bar/legacy` file of the the project if target exists.  

##### `remove` command

- Remove modules.  
    - Remove `foo` module.  
        - Remove `release` version.  
            - Remove module symlinks.  
                -  Delete symlink at `/dir1/foo/stable` directory of the project.  
            - Delete `version_root_dir` at `_modules/foo` directory.  
        - Delete [`module.module_root_dir`](module.md#modulerootdir) at `_modules/foo` directory.  
    - Remove `bar` module.  
        - Remove `latest` version.  
            - Remove module symlinks.  
                -  Delete symlink at `/dir1/subdir1/bar/latest` directory of the project.  
                -  Delete symlink at `/dir2/bar/latest` file of the project.  
                -  Delete symlink at `/dir3/bar/latest` directory of the project.  
            - Delete `version_root_dir` at `_modules/bar/latest` directory.  
        - Remove `stable` version.  
            - Remove module symlinks.  
                -  Delete symlink at `/dir1/subdir1/bar/stable` directory of the project.  
                -  Delete symlink at `/dir2/bar/stable` file of the project.  
            - Delete `version_root_dir` at `_modules/bar/stable` directory.  
        - Remove `v0.1.0` version.  
            - Remove module symlinks.  
                -  Delete symlink at `/dir1/subdir1/bar/v0.1.0` directory of the project.  
                -  Delete symlink at `/dir2/bar/v0.1.0` file of the project.  
            - Delete `version_root_dir` at `_modules/bar/v0.1.0` directory.  
        - Remove `legacy` version.  
            - Remove module symlinks.  
                -  Delete symlink at `/dir1/subdir1/bar/legacy` directory of the project.  
                -  Delete symlink at `/dir2/bar/legacy` file of the project.  
            - Delete `version_root_dir` at `_modules/bar/legacy` directory.  
        - Delete [`module.module_root_dir`](module.md#modulerootdir) at `_modules/bar` directory.  
- Remove project.  
    - Remove project symlinks.  
        -  Delete symlink at `/dir1/root` directory of the project.  

```yaml
project:
  # project_root_dir: /path/to/project
  # project_root_dir: $GITHUB_WORKSPACE
  # remove_project_root_dir_for_commands: setup,remove
  project_src_checkout:
    # checkout_type: git
    src_url: git@github.com:stargateoss/project.git
    git_auth_token_var: GIT_AUTH_TOKEN
    # git_auth_token: ghp_...
    # ref: refs/heads/master
    # fetch_depth: 0
    # fetch_tags: true|false
    # show_progress: true|false
    # lfs: true|false
    submodules: recursive
    # sparse_checkout: |
    #   dir1/
    #   dir2/subdir1
    # sparse_checkout_cone_mode: true|false
    # ssh_strict: true|false
    # persist_credentials: true|false
    # set_safe_directory: add|add_and_remove|ignore
  project_symlinks:
    list:
      root:
        # ignore: true|false
        target: "@PROJECT__ROOT_DIR@"
        # target_expansions: "env,placeholder"
        dest: dir1/root
        # dest_expansions: "env,placeholder"
        # target_is_directory: true|false
        # target_no_exist_mode: ignore|allow|disallow
        # dest_already_exists_mode: ignore|overwrite|overwrite_only_if_symlink|disallow

  modules:
    version_src_checkout:
      git_auth_token_var: GIT_AUTH_TOKEN
      # git_auth_token: ghp_...
    list:
      foo:
        # ignore: true|false
        module_root_dir: _modules/foo
        versions:
          list:
            stable:
              # ignore: true|false
              version_src_checkout:
                # checkout_type: git
                src_url: git@github.com:stargateoss/foo.git
                # src_url: https://github.com/stargateoss/foo.git
                # git_auth_token_var: FOO__STABLE__GIT_AUTH_TOKEN
                # git_auth_token: ghp_...
                ref: refs/heads/master
                # fetch_depth: 0
                # fetch_tags: true|false
                # show_progress: true|false
                # lfs: true|false
                # submodules: disable|enable|recursive
                # sparse_checkout_level_mode: add|override
                sparse_checkout: |
                  dir1/
                  dir2/subdir1
                # sparse_checkout_cone_mode: true|false
                # ssh_strict: true|false
                # persist_credentials: true|false
                # set_safe_directory: add|add_and_remove|ignore
              version_symlinks:
                # symlinks_list_level_mode: add|override
                list:
                  dir1:
                    # ignore: true|false
                    target: ../../@VERSION__ROOT_SUB_DIR@/dir1
                    # target_expansions: "env,placeholder"
                    dest: dir1/foo/@VERSION__NAME@
                    # dest_expansions: "env,placeholder"
                    # target_is_directory: true|false
                    # target_no_exist_mode: ignore|allow|disallow
                    # dest_already_exists_mode: ignore|overwrite|overwrite_only_if_symlink|disallow

      bar:
        # ignore: true|false
        module_root_dir: _modules/bar
        version_src_checkout:
          # checkout_type: git
          src_url: git@github.com:stargateoss/bar.git
          # git_auth_token_var: BAR__GIT_AUTH_TOKEN
          # git_auth_token: ghp_...
          # fetch_depth: 0
          # fetch_tags: true|false
          # show_progress: true|false
          # lfs: true|false
          # submodules: enable|recursive
          sparse_checkout: |
            /dir1/subdir1/*
            /dir2/subfile1
          sparse_checkout_cone_mode: false
          # ssh_strict: true|false
          # persist_credentials: true|false
          # set_safe_directory: add|add_and_remove|ignore
        version_symlinks:
          list:
            dir1/subdir1:
              # ignore: true|false
              target: ../../../@VERSION__ROOT_SUB_DIR@/dir1/subdir1
              # target_expansions: "env,placeholder"
              dest: dir1/subdir1/bar/@VERSION__NAME@
              # target_is_directory: true|false
              # dest_expansions: "env,placeholder"
              target_no_exist_mode: ignore
              # dest_already_exists_mode: ignore|overwrite|overwrite_only_if_symlink|disallow
            dir2/subfile1:
              target: ../../@VERSION__ROOT_SUB_DIR@/dir2/subfile1
              dest: dir2/bar/@VERSION__NAME@
              target_is_directory: false
              target_no_exist_mode: ignore

        versions:
          single_version: false # **important**
          list:
            latest:
              version_src_checkout:
                ref: refs/heads/master
                # ref: refs/pull/1/head
                # ref: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                sparse_checkout_level_mode: add
                sparse_checkout: |
                  /dir3/*
              version_symlinks:
                # symlinks_list_level_mode: add
                list:
                  dir3:
                    target: ../../@VERSION__ROOT_SUB_DIR@/dir3
                    dest: dir3/bar/@VERSION__NAME@
                    dest_already_exists_mode: overwrite

            stable:
              version_src_checkout:
                ref: refs/tags/v0.1.0

            v0.1.0:
              version_src_checkout:
                ref: refs/tags/v0.1.0

            legacy:
              version_src_checkout:
                src_url: git@github.com:stargateoss/bar-legacy.git
                # git_auth_token_var: BAR__LEGACY__GIT_AUTH_TOKEN
                # git_auth_token: ghp_...
                ref: refs/heads/master
                sparse_checkout_level_mode: override
                sparse_checkout: |
                  /legacy-dir1/subdir1/*
                  /legacy-dir2/subfile1
              version_symlinks:
                symlinks_list_level_mode: override
                list:
                  legacy-dir1/subdir1:
                    target: ../../../@VERSION__ROOT_SUB_DIR@/legacy-dir1/subdir1
                    dest: dir1/subdir1/bar/@VERSION__NAME@
                  legacy-dir2/subfile1:
                    target: ../../@VERSION__ROOT_SUB_DIR@/legacy-dir2/subfile1
                    dest: dir2/bar/@VERSION__NAME@
                    target_is_directory: false
```

## &nbsp;

&nbsp;



### Multiple Projects

This can be used to checkout multiple independent projects that are defined in a single `yaml` manifest file instead of defining them in multiple files. Each manifest must end with document end market `\n...\n` followed by a directed end marker `\n---\n`, like `\n...\n---\n`. Check [yaml document markers](https://yaml.org/spec/1.2.2/#912-document-markers) docs for more info.

The [`project.project_root_dir`] must be defined for each project and they should be different, otherwise they would conflict/overwrite each other.

You can also pass multiple manifests in the same manifest file with process substitution, check [Setup single project with manifest passed with process substitution](../index.md#setup-single-project-with-manifest-passed-with-process-substitution) command example.

```yaml
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
```

---

&nbsp;





## Supported Levels and Modes

- Some sub keys exist at only one level.  
    For example, the [`project_src_checkout`](#projectsrccheckout) `dict` for [`src_checkout`](src-checkout.md) is defined at `project` level only, and the [`project_symlinks`](project.md#projectsymlinks) `dict` for [`symlinks`](symlinks.md) is also defined at the `project` level only. The values in it will not be used by any lower level.

- Some sub keys exist at multiple levels and lowest/deepest level a key is defined at will `override` the values of any higher levels by default.  
    For example, the [`version_src_checkout`](version.md#versionsrccheckout) `dict` for [`src_checkout`](src-checkout.md) is defined at `modules`, `module` and `version` levels, and the [`version_symlinks`](version.md#versionsymlinks) `dict` for [`symlinks`](symlinks.md) is defined at the `module` and `version` levels. Any sub keys under the `version_src_checkout` of the `version` level will override the value of the `modules` and `module` level. If no key is defined at the `version` level, like [`version_src_checkout.src_url`](src_checkout.md#srcurl), then the `module` level key will be used instead as src url would normally be the same for all versions of a module.

- Some keys that exist at multiple levels may support values in the lower levels to `add` to the ones at higher levels by default. This mode may be changeable if an additional key `<key_name>_level_mode` also exist that can be set to `override`, etc.  
    For example, the [`version_src_checkout.sparse_checkout`](src_checkout.md#sparsecheckout) value at `version` level will `add` to the value defined at `module` level, unless [`version_src_checkout.sparse_checkout_level_mode`](src_checkout.md#sparsecheckoutlevelmode) is set to `override`, in which case, only `version` level value will be used.

- Some sub keys will not exist at all levels.  
    For example, the [`version_src_checkout.src_url`](src_checkout.md#srcurl) does not exist at the `modules` level, as src urls would either be `module` or `version` specific, but [`version_src_checkout.git_auth_token`](src_checkout.md#gitauthtoken) and [`version_src_checkout.git_auth_token_var`](src_checkout.md#gitauthtokenvar) do exist at `modules`, `module` and `version` levels as they can be shared between different `modules`.

Check each key's **Supported Levels** info, if specified, to know the levels at which a key can be defined that its value is used.

For keys under the `project.` `dict`, except `project.modules`.

- `project` level keys can be defined in the [`project` config](project.md).

For keys under the `project.modules` `dict`.

- `modules` level keys can be defined in the [`modules` config](modules.md).
- `module` level keys can be defined in the [`module` config](module.md).
- `version` level keys can be defined in the [`version` config](version.md).

Check each key's **Level Mode** info, if specified, to know the mode that will be used to set the final value if the key is defined at multiple levels. If not specified, then default mode is that lower levels will `override` the values of any higher level.

---

&nbsp;





## Environmental Variable Expansions

For specific keys like [`project.project_root_dir`], [`module.module_root_dir`](module.md#modulerootdir), [`symlink.target`](symlink.md#target) and [`symlink.dest`](symlink.md#dest), etc, the environmental variable references in the values will be expanded, like `bash` does.

- Substrings of the form `$NAME` or `${NAME}` are replaced by the value of the environmental variable name.
- Substrings of the form `\$NAME` that have escaped `$` character are replaced with the literal value `$NAME` without expansion.
- References to non-existing environmental variables are replaced with an empty string.

---

&nbsp;





[`$GITHUB_WORKSPACE`]: https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
[`actions/checkout`]: https://github.com/actions/checkout
[Current working directory (`cwd`)]: https://www.gnu.org/software/libc/manual/html_node/Working-Directory.html
[`git` submodules]: https://git-scm.com/book/en/v2/Git-Tools-Submodules
[`project.project_root_dir`]: project.md#projectrootdir
