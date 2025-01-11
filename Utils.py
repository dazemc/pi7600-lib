import sys


def py_version_check() -> bool:
    """
    Python minimum version check (3.10)
    :return: bool
    """
    try:
        if float(sys.version[: sys.version[2:].find(".") + 2]) < 3.10:
            print("Python version must be 3.10 or greater")
            print("\nExiting...")
            return False
    except:
        user_input = input(
            "Python version check failed. Depends on 3.10 or greater, continue anyways(y/N?"
        ).lower()
        if user_input in ["", "n"]:
            print("\nExiting...")
            return False
    return True


class SingletonMeta(type):
    """
    This metaclass ensures that only one instance of any class using it exists.
    """

    _instances = {}  # Dictionary to hold single instances

    def __call__(cls, *args, **kwargs):
        """
        If an instance of cls doesn't exist, create one and store it in _instances.
        Otherwise, return the existing instance.
        """
        if cls not in cls._instances:
            # print(f"Creating new instance of {cls.__name__}")
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        else:
            # print(f"Using existing instance of {cls.__name__}")
            pass
        return cls._instances[cls]
