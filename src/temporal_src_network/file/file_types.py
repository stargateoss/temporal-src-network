class FileType():
    "The type of file."

    def __init__(self, name, value):
        self.name = name
        self.value = value

class FileTypes:
    "The types of files"

    NO_EXIST = FileType("no_exist", 0)            # 0000000000
    REGULAR = FileType("regular", 1)              # 0000000001
    DIRECTORY = FileType("directory", 2)          # 0000000010
    SYMLINK = FileType("symlink", 4)              # 0000000100
    SOCKET = FileType("socket", 8)                # 0000001000
    CHARACTER = FileType("character", 16)         # 0000010000
    FIFO = FileType("fifo", 32)                   # 0000100000
    BLOCK = FileType("block", 64)                 # 0001000000
    DOOR = FileType("door", 128)                  # 0010000000
    PORT = FileType("port", 256)                  # 0100000000
    WHITEOUT = FileType("whiteout", 512)          # 1000000000
    UNKNOWN = FileType("unknown", 1073741824)     # 1000000000000000000000000000000

FILE_TYPE_NORMAL_FLAGS = FileTypes.REGULAR.value | FileTypes.DIRECTORY.value | FileTypes.SYMLINK.value
"""Flags to represent regular, directory and symlink file types defined by {@link FileTypes}"""

FILE_TYPE_ANY_FLAGS = 2147483647 # 1111111111111111111111111111111 (31 1's)
"""Flags to represent any file type defined by {@link FileTypes}"""

def convert_file_type_flags_to_names_string(file_type_flags):
    if not file_type_flags or not isinstance(file_type_flags, int):
        return None

    file_type_flags_string = ""
    for file_type in [
            FileTypes.REGULAR, FileTypes.DIRECTORY, FileTypes.SYMLINK, FileTypes.SOCKET,
            FileTypes.CHARACTER, FileTypes.FIFO, FileTypes.BLOCK, FileTypes.UNKNOWN]:
        if (file_type_flags & file_type.value) > 0:
            file_type_flags_string = file_type_flags_string + file_type.name + ","

    if file_type_flags_string.endswith(","):
        file_type_flags_string = file_type_flags_string[:-1]

    return file_type_flags_string
