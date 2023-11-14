# Install

The `temporal-src-network` can be run with `python3`. For dependencies and install instructions, read below.

### Contents

- [Dependencies](#Dependencies)
- [Linux Distros](#Linux-Distros)
- [Termux In Android](#Termux-In-Android)

---

&nbsp;





## Dependencies

1. Android users should install [Termux App](https://github.com/termux/termux-app).

2. `python3` and optionally `pip3` should be installed in your system.
    - Linux distros: `sudo apt install python3 python3-pip`.
    - Termux (non-root shell): `pkg install python`.  Check https://wiki.termux.com/wiki/Python for details. `pip` will automatically be installed.

3. The [`ruamel.yaml`](https://yaml.readthedocs.io) python module is used to load `YAML` manifest files. Check [Install](https://yaml.readthedocs.io/en/latest/install.html) instructions for more info.
    - Linux distros: `sudo pip3 install ruamel.yaml`.
    - Termux (non-root shell): `pip3 install ruamel.yaml`.

---

&nbsp;





## Linux Distros System

The `temporal-src-network` file should be placed in the `/usr/local/bin` directory if you want to install it system-wide for all users as per [FHS 3.0](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch04s09.html). It should have readable `755` permission before it can be executed.  

The install command for `curl`  is for Ubuntu/Debian, it may be different for other distros.  

&nbsp;

### Basic

Download `temporal-src-network.zip` from the **`latest` [GitHub releases](https://github.com/stargateoss/temporal-src-network/releases)** and convert it into an executable.

```shell
sudo apt install curl && \
export install_path="/usr/local/bin" && \
sudo mkdir -p "$install_path" && \
sudo rm -f "$install_path/temporal-src-network.zip" && \
sudo curl -L 'https://github.com/stargateoss/temporal-src-network/releases/latest/download/temporal-src-network.zip' -o "$install_path/temporal-src-network.zip" && \
echo '#!/usr/bin/env python3' | cat - "$install_path/temporal-src-network.zip" | sudo tee "$install_path/temporal-src-network" > /dev/null && \
sudo rm -f "$install_path/temporal-src-network.zip" && \
sudo chmod 755 "$install_path/temporal-src-network";
```

## &nbsp;

&nbsp;



### Advance

1. Export install directory path and create it and delete any existing `temporal-src-network.zip` file.  

```shell
export install_path="/usr/local/bin" && \
mkdir -p "$install_path" && \
sudo rm -f "$install_path/temporal-src-network.zip"
```

2. Download the `temporal-src-network.zip` file.  

    - **Using `curl` from [GitHub releases](https://github.com/stargateoss/temporal-src-network/releases)** with a non-root termux shell.  
        Run `pkg install curl` to install `curl` first.  
        - Latest release:  

            `curl -L 'https://github.com/stargateoss/temporal-src-network/releases/latest/download/temporal-src-network.zip' -o "$install_path/temporal-src-network.zip"`  

        - Specific release:  

            `curl -L 'https://github.com/stargateoss/temporal-src-network/releases/download/v0.1.0/temporal-src-network.zip' -o "$install_path/temporal-src-network.zip"`  

    - **Manually from [GitHub releases](https://github.com/stargateoss/temporal-src-network/releases)** listed under the `Assets` dropdown menu to the linux download directory and then copy it to install directory using `cat` command or a root file browser (like `sudo nautilus`).  

        `cat "$HOME/Downloads/temporal-src-network.zip" | sudo tee "$install_path/temporal-src-network.zip" > /dev/null`  

    - **Manually from [GitHub Build Action](https://github.com/stargateoss/temporal-src-network/actions/workflows/debug_build.yml?query=branch%3Amaster+event%3Apush)** with the `temporal-src-network-build` listed under the `Artifacts` section of a workflow run to the linux download directory and then copy it to install directory using `zip` command or a root file browser (like `sudo nautilus`). These are created for each commit/push done to the repository and can be used by users who don't want to wait for releases and want to try out the latest features immediately or want to test their pull requests.  

        Note that you need to be [**logged into a `Github` account**](https://github.com/login) for the `Artifacts` links to be enabled/clickable. If you are using the [`Github` app](https://github.com/mobile), then make sure to open workflow link in a browser like Chrome or Firefox that has your Github account logged in since the in-app browser may not be logged in.  

        `unzip -p "$HOME/Downloads/temporal-src-network-build.zip" temporal-src-network.zip  | sudo tee "$install_path/temporal-src-network.zip" > /dev/null`  

3. Create `temporal-src-network` executable file as per [this blog](http://blog.ablepear.com/2012/10/bundling-python-files-into-stand-alone.html).

    - Create executable file from the `temporal-src-network.zip` file and then delete original:  

        `echo '#!/usr/bin/env python3' | cat - "$install_path/temporal-src-network.zip" | sudo tee "$install_path/temporal-src-network" > /dev/null && rm -f "$install_path/temporal-src-network.zip"`

    - Create a wrapper `sh` shell script that will execute the `temporal-src-network.zip` file with a `python3` shell. This method will require `2` files to be kept in the install directory.

        `printf "%s\n\n%s\n" '#!/usr/bin/env sh' "python3 '$install_path/temporal-src-network.zip'"' "$@"' | sudo tee "$install_path/temporal-src-network" > /dev/null`

4. Set readable permissions.  

    - Set ownership and permissions with `chown` and `chmod` commands respectively:  

        `sudo chmod 755 "$install_path/temporal-src-network"`  

---

&nbsp;





## Termux In Android

The `temporal-src-network` file should be installed in termux `bin` directory `/data/data/com.termux/files/usr/bin`. It should have `termux` `uid:gid` ownership and have readable `700` permission before it can be executed.  

&nbsp;

### Basic

Download `temporal-src-network.zip` from the **`latest` [GitHub releases](https://github.com/stargateoss/temporal-src-network/releases)** and convert it into an executable.

```shell
pkg install curl && \
export install_path="/data/data/com.termux/files/usr/bin" && \
mkdir -p "$install_path" && \
rm -f "$install_path/temporal-src-network.zip" && \
curl -L 'https://github.com/stargateoss/temporal-src-network/releases/latest/download/temporal-src-network.zip' -o "$install_path/temporal-src-network.zip" && \
echo '#!/usr/bin/env python3' | cat - "$install_path/temporal-src-network.zip" > "$install_path/temporal-src-network" && \
rm -f "$install_path/temporal-src-network.zip" && \
export owner="$(stat -c "%u" "$install_path")"; chown "$owner:$owner" "$install_path/temporal-src-network" && \
chmod 700 "$install_path/temporal-src-network";
```

## &nbsp;

&nbsp;



### Advance

1. Export install directory path and create it and delete any existing `temporal-src-network.zip` file.  

```shell
export install_path="/data/data/com.termux/files/usr/bin" && \
mkdir -p "$install_path" && \
rm -f "$install_path/temporal-src-network.zip"
```

2. Download the `temporal-src-network.zip` file.  

    - **Using `curl` from [GitHub releases](https://github.com/stargateoss/temporal-src-network/releases)** with a non-root termux shell.  
        Run `pkg install curl` to install `curl` first.  
        - Latest release:  

            `curl -L 'https://github.com/stargateoss/temporal-src-network/releases/latest/download/temporal-src-network.zip' -o "$install_path/temporal-src-network.zip"`  

        - Specific release:  

            `curl -L 'https://github.com/stargateoss/temporal-src-network/releases/download/v0.1.0/temporal-src-network.zip' -o "$install_path/temporal-src-network.zip"`  

    - **Manually from [GitHub releases](https://github.com/stargateoss/temporal-src-network/releases)** listed under the `Assets` dropdown menu to the android download directory and then copy it to install directory using `cat` command or a root file browser.  

       `cat "/storage/emulated/0/Download/temporal-src-network.zip" > "$install_path/temporal-src-network.zip"`  

    - **Manually from [GitHub Build Action](https://github.com/stargateoss/temporal-src-network/actions/workflows/debug_build.yml?query=branch%3Amaster+event%3Apush)** with the `temporal-src-network-build` artifact listed under the `Artifacts` section of a workflow run to the android download directory and then copy it to install directory using `zip` command or a root file browser. These are created for each commit/push done to the repository and can be used by users who don't want to wait for releases and want to try out the latest features immediately or want to test their pull requests.  

        Note that you need to be [**logged into a `Github` account**](https://github.com/login) for the `Artifacts` links to be enabled/clickable. If you are using the [`Github` app](https://github.com/mobile), then make sure to open workflow link in a browser like Chrome or Firefox that has your Github account logged in since the in-app browser may not be logged in.  

        `unzip -p "/storage/emulated/0/Download/temporal-src-network-build.zip" temporal-src-network.zip > "$install_path/temporal-src-network.zip"`  

3. Create `temporal-src-network` executable file as per [this blog](http://blog.ablepear.com/2012/10/bundling-python-files-into-stand-alone.html).

    - Create executable file from the `temporal-src-network.zip` file and then delete original:  

        `echo '#!/usr/bin/env python3' | cat - "$install_path/temporal-src-network.zip" > "$install_path/temporal-src-network" && rm -f "$install_path/temporal-src-network.zip"`

    - Create a wrapper `sh` shell script that will execute the `temporal-src-network.zip` file with a `python3` shell. This method will require `2` files to be kept in the install directory.

        `printf "%s\n\n%s\n" '#!/usr/bin/env sh' "python3 '$install_path/temporal-src-network.zip'"' "$@"' > "$install_path/temporal-src-network"`

4. Set `termux` ownership and readable permissions.  

    - If you used a `curl` or `cat` to copy the file, then use a non-root termux shell to set ownership and permissions with `chown` and `chmod` commands respectively:  

        `export owner="$(stat -c "%u" "$install_path")"; for f in temporal-src-network temporal-src-network.zip; do test -f "$install_path/$f" && chown "$owner:$owner" "$install_path/$f" && chmod 700 "$install_path/$f"; done`  

    - If you used a root file browser to copy the file, then use `su` to start a root shell to set ownership, permissions and selinux context for termux with `chown`, `chmod` and `restorecon` commands respectively:  

        `export owner="$(stat -c "%u" "$install_path")"; su -c "for f in temporal-src-network temporal-src-network.zip; do test -f "$install_path/$f" && chown \"$owner:$owner\" \"$install_path/$f\" && chmod 700 \"$install_path/$f\" && restorecon \"$install_path/$f\"; done";`  

    - Or manually set them with your root file browser. You can find `termux` `uid` and `gid` by running the command `id -u` in a non-root termux shell or by checking the properties of the termux `bin` directory from your root file browser.  

---

&nbsp;
