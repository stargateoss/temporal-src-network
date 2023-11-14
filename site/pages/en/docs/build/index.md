# Build

The `temporal-src-network` is not a single python script and its sources contain multiple files and modules under the `src` directory.

To call `temporal-src-network` `main()` method directly while inside the repository for testing, you can execute `src/__main__.py` and pass it any arguments, like `src/__main__.py setup /path/to/manifest.yaml`.

To build `temporal-src-network` sources into an executable file as per [this blog](http://blog.ablepear.com/2012/10/bundling-python-files-into-stand-alone.html), you can do one of the following.

1. Create a zip file of the sources that can be executed with the `python3` shell like `python3 /path/to/temporal-src-network`. The zip file can be opened in any zip viewer to view the sources.  

	```shell
	rm -f temporal-src-network.zip && \
	(cd src; zip -r ../temporal-src-network.zip *) && \
	mv temporal-src-network.zip temporal-src-network
	```

&nbsp;



2. Create a zip file of the sources and then create an executable file (self-extracting zip) from it by inserting the `python3` shebang at the start of the zip file so that it can be executed directly like `/path/to/temporal-src-network` or as `temporal-src-network` if under `$PATH`.  

	```shell
	rm -f temporal-src-network.zip && \
	(cd src; zip -r ../temporal-src-network.zip *) && \
	echo '#!/usr/bin/env python3' | cat - temporal-src-network.zip > temporal-src-network && \
	rm -f temporal-src-network.zip && \
	chmod +x temporal-src-network
	```

    The `temporal-src-network` executable file will fail to open by standard zip viewers, unless shebang is removed by converting it back to a standard zip file by running `sed -zE -e 's|^\#\!/usr/bin/env python3[\n]||' temporal-src-network > temporal-src-network.zip`.  

&nbsp;



3. Create a wrapper `sh` shell script that will execute the `temporal-src-network.zip` file in the current directory (`cwd`, not shell script directory) with a `python3` shell. This method will require `2` files to be kept. Replace full path to zip in `python3 temporal-src-network.zip` if different from current directory, like [install](../install/index.md) docs do.  

	```shell
	rm -f temporal-src-network.zip && \
	(cd src; zip -r ../temporal-src-network.zip *) && \
	printf "%s\n\n%s\n" '#!/usr/bin/env sh' 'python3 temporal-src-network.zip "$@"' > temporal-src-network
	chmod +x temporal-src-network
	```

	If you do not want to hard code the zip path and both zip and wrapper shell script will be in the same directory, you can also dynamically get their parent directories, but `bash` should be used for stability of correct path instead of `sh`.  

	```shell
	rm -f temporal-src-network.zip && \
	(cd src; zip -r ../temporal-src-network.zip *) && \
	printf "%s\n\n%s\n" '#!/usr/bin/env bash' 'python3 "$(dirname "$(readlink -f -- "$0")")"/temporal-src-network.zip "$@"' > temporal-src-network
	chmod +x temporal-src-network
	```

---

&nbsp;
