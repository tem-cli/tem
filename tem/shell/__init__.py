import enum
import os


class Shell(enum.Enum):
    FISH = "fish"
    BASH = "bash"
    ZSH = "zsh"
    SH = "sh"
    NONE = None

    def __bool__(self):
        return bool(self.value)

    def __str__(self):
        return self.value


def shell() -> Shell:
    return Shell(os.environ.get("TEM_SHELL"))