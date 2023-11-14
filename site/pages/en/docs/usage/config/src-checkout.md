# Source Checkout Config

The `src_checkout` config is defined in the `project.project_src_checkout` `dict` key for checking out the `project` and in the `project.modules.version_src_checkout`, `project.modules.list.<module_name>.version_src_checkout` and `project.modules.list.<module_name>.versions.<version_name>.version_src_checkout` `dict` keys to checkout a `version`. It contains the config for how to checkout or download an external source version for `temporal-src-network` `setup` commands. The name *checkout* refers to the [`git checkout`](https://git-scm.com/docs/git-checkout) command and the [`actions/checkout`] workflow action (whose code is ported by `temporal-src-network`), but it does not mean that only `git` source [checkout_type](#checkout_type) can be supported, and it is planned to add support to download `zip`, `tar` or `raw` files.

See also [`Supported Levels and Modes`](index.md#supported-levels-and-modes) for more info on **Supported Levels** and **Level Mode** info of keys.

The **Supported Checkout Types** means the [`checkout_types`](#checkout_type) for which the key can be used.

### Contents

- [Keys](#keys)
    - [`checkout_type`](#checkouttype)
    - [`src_url`](#srcurl)
    - [`git_auth_token`](#gitauthtoken)
    - [`git_auth_token_var`](#gitauthtokenvar)
    - [`ref`](#ref)
    - [`fetch_depth`](#fetchdepth)
    - [`fetch_tags`](#fetchtags)
    - [`show_progress`](#showprogress)
    - [`lfs`](#lfs)
    - [`submodules`](#submodules)
    - [`sparse_checkout`](#sparsecheckout)
    - [`sparse_checkout_cone_mode`](#sparsecheckoutconemode)
    - [`sparse_checkout_skip_checks`](#sparsecheckoutskipchecks)
    - [`sparse_checkout_level_mode`](#sparsecheckoutlevelmode)
    - [`ssh_strict`](#sshstrict)
    - [`persist_credentials`](#persistcredentials)
    - [`set_safe_directory`](#set_safe_directory)

---

&nbsp;





## Keys

The following keys are supported.

&nbsp;

### checkout_type

The source checkout type with which to checkout or download the [`src_url`](#srcurl).

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

`ignore` - Ignore checking out.

`git` - A `git` repository. **Requires `git` version `>= 2.18` to be in `$PATH`. REST API fallback like [`actions/checkout`] is currently not supported.**

**Examples:**

```yaml
version_src_checkout:
  # The source is a git repository
  checkout_type: git
```

## &nbsp;



### src_url

The url of the source from which to checkout our download the source. This can be a url to any repository host like GitHub, GitLab, etc.

 If a token is set in [`git_auth_token`](#gitauthtoken) or the token is exported in the environmental variable set in [`git_auth_token_var`](#gitauthtokenvar), then `git@` ssh urls will be replaced with `https` urls automatically so that the token can be used with `http.<src_url>.extraheader` `git` config to fetch repos. If token is not set or not exported, like by local builds, then `git@` ssh urls will be used as is to fetch repos with ssh keys configured by the user themselves in their `~/.ssh` directory. The [`actions/checkout`] action does this replacement when `ssh-key` is set instead, but `ssh-key` is currently not supported. For example, `git@github.com:` will be replaced with `https://github.com/`.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `git`

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

`git` [`checkout_type`](#checkout_type) - A valid `git` repository url, normally a `https://` or `file://` url or a `git@` ssh url, like to a [GitHub](https://github.com) or [GitLab](https://gitlab.com) repository. ([1](https://github.com/git/git/blob/v2.42.0/urlmatch.c), [2](https://github.com/git/git/blob/v2.42.0/t/t0110-urlmatch-normalization.sh))

**Examples:**

```yaml
version_src_checkout:
  # A GitHub ssh url
  src_url: git@github.com:stargateoss/foo
  # A GitHub https url
  src_url: https://github.com/stargateoss/foo.git
  # A GitLab ssh url
  src_url: git@gitlab.com:stargateoss/foo
```

## &nbsp;



### git_auth_token

The authentication token to use for `http.<src_url>.extraheader` `git` config to fetch the `git` repo if [`src_url`](srcurl) is a `https` url.

**If value is set, then a `ssh` repo url will also be automatically converted to a `https` url, check [`src_url`](srcurl) for more info.**

**The [`git_auth_token_var`](#gitauthtokenvar) value takes precedence over this if it is set.**

**DO NOT use this if the manifest will be publicly viewable, like on a GitHub public repo.** Use it only for private or local repos. Prefer to use [`git_auth_token_var`](#gitauthtokenvar) instead, especially for workflow actions. However, you can may use it if dynamically generating or modifying the manifest file with the token inside a workflow action.

The actual token value in the manifest or env is not logged by `temporal-src-network`, even for verbose log levels and is logged as `***` if set for security reasons. It is also not passed as command line argument to `git config`. A placeholder value will first be passed to `git config` for the `http.<src_url>.extraheader` config and then the placeholder value will be replaced with the actual value in the `.git/config` file after opening the file with the [`io.open()`](https://docs.python.org/3/library/io.html#io.open) call in write mode. Check [`Command line process auditing`](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/command-line-process-auditing) for more info.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `git`

**Related keys:** [`git_auth_token_var`](#gitauthtokenvar), [`src_url`](srcurl), [`persist_credentials`](persistcredentials)

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`modules`, `module`, `version`)

**Values:**

The characters for the token.

**Examples:**

```yaml
project:
  modules:
    version_src_checkout:
      git_auth_token_var: GIT_AUTH_TOKEN
    list:
      foo:
        versions:
          list:
            stable:
              version_src_checkout:
                # Use git_auth_token to get foo repo with https url
                src_url: https://github.com/stargateoss/foo.git
                git_auth_token: ghp_...

      bar:
        version_src_checkout:
          src_url: git@github.com:stargateoss/bar.git
        versions:
          list:
            latest:
              version_src_checkout:
                # If GIT_AUTH_TOKEN env variable is exported,
                # use token in it to get bar repo with https url
                # after its automatic conversion from ssh url.
                # If not exported, then get bar repo
                # with its ssh url with with ssh keys
                # configured by the user themselves in
                # their `~/.ssh` directory.
            stable:
              version_src_checkout:
                # Same as latest version above.
            v0.1.0:
              version_src_checkout:
                # Same as latest version above.
            legacy:
              version_src_checkout:
                # Use token set in BAR__LEGACY__GIT_AUTH_TOKEN
                # env variable to get bar-legacy repo with https url
                src_url: https://github.com/stargateoss/bar-legacy.git
                git_auth_token_var: BAR__LEGACY__GIT_AUTH_TOKEN
```

## &nbsp;



### git_auth_token_var

The exported environmental variable from which to read the authentication token to use for `http.<src_url>.extraheader` `git` config to fetch the `git` repo if [`src_url`](srcurl) is a `https` url.

**If the environmental variable defined is set to a token at runtime, then a `ssh` repo url will also be automatically converted to a `https` url, check [`src_url`](srcurl) for more info.**

**This will take precedence over the [`git_auth_token`](#gitauthtoken) value if set.** Prefer to use this instead of [`git_auth_token`](#gitauthtoken), especially for workflow actions.

If using `temporal-src-network` in a GitHub workflow to only [checkout out the project/repository that hosts the workflow without any modules](index.md#standalone-project), then you should set `git_auth_token_var` to `$GITHUB_TOKEN` as it will have sufficient permissions to checkout the repository. Check [automatic token authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication) GitHub docs.

However, if using `temporal-src-network` in a GitHub workflow to [checkout out external modules/repositories that do not host the workflow](index.md#project-with-single-module), then you should set `git_auth_token_var` to a custom environmental variables like `$GIT_AUTH_TOKEN` that contains a custom Personal Access Token, as `$GITHUB_TOKEN` **will not** have sufficient permissions to checkout the repository. Check [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) GitHub docs on how to generate the token. The token must have `repo.public_repo` scope to checkout public repositories or `repo` scope to checkout private repositories, check [Scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes) GitHub docs. The token should be stored in GitHub secrets and can be exported with the [`env` key](https://docs.github.com/en/actions/learn-github-actions/variables#defining-environment-variables-for-a-single-workflow) of the action, check [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions) GitHub docs. **Do not** pass token as command line arguments as it may be viewable by other users, check [`Command line process auditing`](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/command-line-process-auditing) for more info. Moreover, if using [process substitution](../index.md#setup-single-project-with-manifest-passed-with-process-substitution) to pass the manifest file, then the heredoc may create a physical file in `$TMPDIR` for the manifest, which will be readable by other users.

```yaml
steps:
  - name: Checkout repository
  env:
    GIT_AUTH_TOKEN: ${{ secrets.GIT_AUTH_TOKEN }}
```

See also [python `os.environ()`](https://docs.python.org/3/library/os.html#os.environ) docs.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `git`

**Related keys:** [`git_auth_token`](#gitauthtoken), [`src_url`](srcurl), [`persist_credentials`](persistcredentials)

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`modules`, `module`, `version`)

**Values:**

The name of the exported environmental variable. If name starts with the dollar `$` character, then it will automatically be trimmed.

**Examples:**

Check examples for [`git_auth_token`](#gitauthtoken).

## &nbsp;



### ref

The [`git` reference](https://git-scm.com/book/en/v2/Git-Internals-Git-References) of the repository to checkout.

See also [`GITHUB_REF`](https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables).

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** Default branch of `git` repository if unset.

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

branch - `refs/heads/<branch_name>`.

tag - `refs/tags/<tag_name>`.

pull request - `refs/pull/<pr_number>/head` or `refs/pull/<pr_number>/merge`. The `refs/pull/<pr_number>/merge` is a reference created by some sites like GitHub to keep track of what would happen if a pull request was merged. It references the merge commit between  `refs/pull/<pr_number>/head` and the destination branch (e.g. `master`).

commit - Commit hash (SHA) with `40` characters in the range `a-zA-Z0-9`.

**Examples:**

```yaml
version_src_checkout:
  # Checkout default branch
  ref:

  # Checkout `master` branch
  ref: refs/heads/master

  # Checkout `v0.1.0` tag
  ref: refs/tags/v0.1.0

  # Checkout `#1` pull request
  ref: refs/pull/1/head

  # Checkout commit
  ref: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## &nbsp;



### fetch_depth

Number of commits to fetch (`--depth` argument for [`git-fetch`](https://git-scm.com/docs/git-fetch)). `0` indicates all history for all branches and tags.

**Type:** `int`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `1`

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

An int value `>= 0`.

**Examples:**

```yaml
version_src_checkout:
  # Fetch all branches and tags
  fetch_depth: 0
```

## &nbsp;



### fetch_tags

Whether to fetch tags, even if [`fetch_depth`](#fetchdepth) is `> 0`. (`--no-tags` argument for [`git-fetch`](https://git-scm.com/docs/git-fetch)).

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `false`

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `true` - Fetch tags.

- `false` - Do not fetch tags.

**Examples:**

```yaml
version_src_checkout:
  # Fetch tags
  fetch_tags: true
```

## &nbsp;



### show_progress

Whether to show progress for:

- `git` - [`git-fetch`](https://git-scm.com/docs/git-fetch) and [`git-checkout`](https://git-scm.com/docs/git-checkout) commands.

**It requires [`verbose` (`-vv`)]((../index.md#help)) log level.**

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `false`

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `true` - Show progress.

- `false` - Do not show progress.

**Examples:**

```yaml
version_src_checkout:
  # Show progress
  show_progress: true
```

## &nbsp;



### lfs

Whether to download [`git` LFS](https://git-lfs.com/) files.

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `false`

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `true` - Download.

- `false` - Do not download.

**Examples:**

```yaml
version_src_checkout:
  # Download LFS files
  lfs: true
```

## &nbsp;



### submodules

Whether to checkout [`git` submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `disable`

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `disable` - Do not download submodules.

- `enable` - Download submodules.

- `recursive` - Download submodules recursively (`--recursive` argument for [`git-submodule`](https://git-scm.com/docs/git-submodule)).

**Examples:**

```yaml
version_src_checkout:
  # Download submodules
  submodules: enable

  # Download submodules recursively
  submodules: recursive
```

## &nbsp;



### sparse_checkout

Whether to perform [`git` sparse checkout](https://git-scm.com/docs/git-sparse-checkout) for the specified files or patterns depending on [`sparse_checkout_cone_mode`](#sparsecheckoutconemode) value.

Check following for how [`cone`] and [`no-cone`] modes work internally and how sparse checkouts can significantly decrease checkout times and reduce repo size and why `cone` mode may be preferred unless exact matches are required.

- [Bring your monorepo down to size with sparse-checkout (GitHub blog)](https://github.blog/2020-01-17-bring-your-monorepo-down-to-size-with-sparse-checkout)
- [`INTERNALS - NON-CONE PROBLEMS`](https://git-scm.com/docs/git-sparse-checkout#_internalsnon_cone_problems)
- [`INTERNALS - CONE MODE HANDLING`](https://git-scm.com/docs/git-sparse-checkout#_internalscone_mode_handling)
- [`INTERNALS - FULL PATTERN SET`](https://git-scm.com/docs/git-sparse-checkout#_internalsfull_pattern_set)
- [`INTERNALS - CONE PATTERN SET`](https://git-scm.com/docs/git-sparse-checkout#_internalscone_pattern_set)
- [`INTERNALS - SUBMODULES`](https://git-scm.com/docs/git-sparse-checkout#_internalssubmodules)
- [`gitignore - PATTERN FORMAT`](https://git-scm.com/docs/gitignore#_pattern_format)

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `false`

**Related keys:** [`sparse_checkout_cone_mode`](#sparsecheckoutconemode), [`sparse_checkout_skip_checks`](#sparsecheckoutskipchecks)

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Level Mode**: [`sparse_checkout_level_mode`](#sparsecheckoutlevelmode)

**Values:**

The newline separated list of directories (`cone`) if [`sparse_checkout_cone_mode`](#sparsecheckoutconemode) equals `true`, otherwise newline separated list of patterns (`no-cone`).

#### Cone mode

The list of directories to match. Only directories should be specified, and not regular files, use [`no-cone`] mode instead if regular files are required.

For any directory specified, all paths below that directory will be included, and any paths immediately under leading directories (including the top-level directory) will also be included. Thus, if `dir2/subdir1/` is specified, then the sparse checkout would contain:  
- All files in the top-level directory.
- All files immediately under `dir2/`.
- All files at any depth under `dir2/subdir1/`.

Older versions also have bugs where specifying `dir/` would also match `foo/dir`, unless `/dir/` is used, which isn't allowed on newer versions. So if `git` version may be older and/or exact matches are required, use [`no-cone`] mode instead.

The `git sparse-checkout --skip-checks` was added as hidden flag in [`git` `v2.36` (`2022/04/18`)](https://git-scm.com/docs/git-sparse-checkout/2.36.0), which can be passed by setting [`sparse_checkout_skip_checks`](#sparsecheckoutskipchecks) to `true`. ([1](https://github.com/git/git/commit/8dd7c4739bded62175bea1f7518d993b39b51f90), [2](https://github.com/git/git/commit/4ce504360bc3b240e570281fabe00a85027532c3))

In `git` version `>= 2.36`, the following errors will be generated:  
- Directory is passed with a leading slash: `specify directories rather than patterns (no leading slash)`  
- Directory is passed with a leading exclamation mark: `specify directories rather than patterns.  If your directory starts with a '!', pass --skip-checks`  
- Directory is passed with a pattern match character: `specify directories rather than patterns.  If your directory really has any of '*?[]\' in it, pass --skip-checks`  
- A file path is passed instead of a directory: `'<file_path>' is not a directory; to treat it as a directory anyway, rerun with --skip-checks`  

#### No Cone mode

The list of patterns to match. It uses `gitignore-style` patterns to select what to **include** (with the exception of negated patterns), while `.gitignore` files use `gitignore-style` patterns to select what to **exclude** (with the exception of negated patterns).

Note that if you want to include a directory in the root directory of the `repo`, then either use `/dir/` with leading `/` or use `dir/*` with trailing `/*` to ensure only the directory in root directory is matched. If you instead use `dir/`, then `foo/dir` will also be matched. The `/` after `dir` is necessary so that only directories are matched, and not regular files.

In `git` version `>= 2.36`, the following warning will be generated:  
- File path is passed without a leading slash: `pass a leading slash before paths such as '<file_pattern>' if you want a single file.`  

**Examples:**

```yaml
project:
  modules:
    list:
      foo:
        versions:
          list:
            stable:
              version_src_checkout:
                # Sparse checkout with cone mode the `/dir1` and `/dir2/subdir1` directories
                sparse_checkout: |
                  dir1/
                  dir2/subdir1/

      bar:
        version_src_checkout:
          sparse_checkout: |
            /dir1/subdir1/*
            /dir2/subfile1
          sparse_checkout_cone_mode: false

        versions:
          list:
            latest:
              version_src_checkout:
                # Sparse checkout with no-cone mode the `/dir1/subdir1` and `/dir3` directories and `/dir2/subfile1` file
                sparse_checkout_level_mode: add
                sparse_checkout: |
                  /dir3/*

            stable:
              version_src_checkout:
                # Sparse checkout with no-cone mode the `/dir1/subdir1` directory and `/dir2/subfile1` file

            v0.1.0:
              version_src_checkout:
                # Sparse checkout with no-cone mode the `/dir1/subdir1` directory and `/dir2/subfile1` file

            legacy:
              version_src_checkout:
                # Sparse checkout with no-cone mode the `/legacy-dir1/subdir1` directory and `/legacy-dir2/subfile1` file
                sparse_checkout_level_mode: override
                sparse_checkout: |
                  /legacy-dir1/subdir1/*
                  /legacy-dir2/subfile1
```

## &nbsp;



### sparse_checkout_cone_mode

Whether to use [`cone`] or [`no-cone`] mode for [`sparse_checkout`](#sparsecheckout).

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `true`

**Related keys:** [`sparse_checkout`](#sparsecheckout), [`sparse_checkout_skip_checks`](#sparsecheckoutskipchecks)

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `true` - The value of [`sparse_checkout`](#sparsecheckout) is considered a list of directories for `cone` mode. **Requires `git` version `>= 2.26` to be in `$PATH`.**

- `false` - The value of [`sparse_checkout`](#sparsecheckout) is considered a list of patterns for `no-cone` mode.

**Examples:**

```yaml
version_src_checkout:
  # Use no-cone mode
  sparse_checkout_cone_mode: false
```

## &nbsp;



### sparse_checkout_skip_checks

Whether to pass the `--skip-checks` hidden flag to `git sparse-checkout` if [`sparse_checkout_cone_mode`](#sparsecheckoutconemode) is `true`. Check [`sparse_checkout`](#sparsecheckout) docs for why this may be required.

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `true`

**Related keys:** [`sparse_checkout`](#sparsecheckout), [`sparse_checkout_cone_mode`](#sparsecheckoutconemode)

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `true` - Pass `--skip-checks`. **Requires `git` version `>= 2.36` to be in `$PATH`, otherwise flag is not passed.**

- `false` - Do not pass `--skip-checks`.

**Examples:**

```yaml
version_src_checkout:
  # Skip checks
  sparse_checkout_skip_checks: false
```

## &nbsp;



### sparse_checkout_level_mode

The [`Levels Mode`] mode for the [`sparse_checkout`](#sparsecheckout) key.

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `add`

**Related keys:** [`sparse_checkout`](#sparsecheckout)

**Supported Checkout Types**: `git`

**Supported Levels**: `version`

**Values:**

- `add` - The value of [`sparse_checkout`](#sparsecheckout) at `version` level will be added to any value at `module` level.

- `override` - The value of [`sparse_checkout`](#sparsecheckout) at `version` level will override any value at `module` level.

**Examples:**

Check examples for [`sparse_checkout`](#sparsecheckout).

## &nbsp;

&nbsp;



### ssh_strict

Whether to perform strict host key checking by adding `StrictHostKeyChecking=yes` to `GIT_SSH_COMMAND` for `git` usage.

If not `true` and if `ssh` keys are not already configured in `known_hosts`, then commands will hang forever until input is provided for authenticity prompt like following.

```
The authenticity of host 'github.com (ip)' can't be established.
Are you sure you want to continue connecting (yes/no)?
```

See also [`ssh_config`](https://man7.org/linux/man-pages/man5/ssh_config.5.html) [`git`](https://git-scm.com/docs/git#Documentation/git.txt-codeGITSSHCOMMANDcode) man page.

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `false`

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `true` - Use strict mode.

- `false` - Do not use strict mode.

**Examples:**

```yaml
ssh_strict:
  # Do not use strict mode
  ssh_strict: false
```

## &nbsp;



### persist_credentials

Whether to persist the [`git_auth_token`](#gitauthtoken) or [`git_auth_token_var`](#gitauthtokenvar) with the local `git` config after checkout is complete.

**Currently, `temporal-src-network` does not persist token for repo submodules like [`actions/checkout`] does. ([1](https://github.com/actions/checkout/blob/v4.1.1/src/git-source-provider.ts#L243), [2](https://github.com/actions/checkout/blob/v4.1.1/src/git-auth-helper.ts#L151))**

**Type:** `boolean`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `false`

**Related keys:** [`git_auth_token`](#gitauthtoken)

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `true` - Persist credentials.

- `false` - Do not persist credentials.

**Examples:**

```yaml
persist_credentials:
  # Persist credentials
  persist_credentials: true
```

## &nbsp;



### set_safe_directory

Whether to add `git` repo root directory to the `safe.directory` global `git` config. If not `true`, then `git` may throw `fatal: unsafe repository ('<repo>' is owned by someone else)` errors in certain situations.

Check [Git security vulnerability announced (GitHub blog)](https://github.blog/2022-04-12-git-security-vulnerability-announced) for more info.

**Currently, `temporal-src-network` will not create a temp `$HOME` to set the global `git` config like [`actions/checkout`] does and `set_safe_directory` default to `false` as well.** Instead, with the `add_and_remove` value, the value will automatically be removed after checkout if needed. See also [`actions/checkout`] commits ([1](https://github.com/actions/checkout/commit/dcd71f646680f2efd8db4afa5ad64fdcba30e748), [2](https://github.com/actions/checkout/commit/0ffe6f9c5599e73776da5b7f113e994bc0a76ede)), [pull request `#762`](https://github.com/actions/checkout/pull/762) and [issue `#760`](https://github.com/actions/checkout/issues/760).

**Type:** `string`

**Commits:** [`11be2d80`](https://github.com/stargateoss/temporal-src-network/commit/11be2d80)

**Version:** [`>= 0.1.0`]

**Default:** `ignore`

**Supported Checkout Types**: `git`

**Supported Levels**: (`project`) and (`module`, `version`)

**Values:**

- `add` - Add safe directory but do not remove it after checkout.

- `add_and_remove` - Add safe directory and remove it after checkout. If value already existed in global `git` config before `temporal-src-network` command was run, it will still be removed as inter-process concurrency cannot be maintained anyways.

- `ignore` - Do not add safe directory.

**Examples:**

```yaml
set_safe_directory:
  # Add and remove safe directory
  set_safe_directory: add_and_remove
```

---

&nbsp;





[`actions/checkout`]: https://github.com/actions/checkout
[`cone`]: #cone-mode
[`no-cone`]: #no-cone-mode
[`Levels Mode`]: index.md#supported-levels-and-modes

[`>= 0.1.0`]: https://github.com/stargateoss/temporal-src-network/releases/tag/v0.1.0
