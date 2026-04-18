import os
import sys
from pathlib import Path

from Constants import Strings


class Fetch:
    """
    Helper for getting icons from resource files.
    """

    @staticmethod
    def get_resource_path(name: str) -> str:
        """
        Return a string absolute path of a resource from the Resources folder or elsewhere.
        :param name: Name of the resource to get or path.
        :return: Path to the resource on disk.
        :raise FileNotFoundError: if resource is not found
        """
        if os.path.exists(name):
            # If the name is a path that already leads to a file return that as an absolute path.
            return os.path.abspath(name)
        else:
            # Assume it is a resource from the Resources folder.
            path = Path(os.path.abspath(sys.path[0]))
            resource_path = os.path.realpath(os.path.join(path, 'Resources', name))
            if os.path.exists(resource_path):
                return resource_path
            else:
                raise FileNotFoundError(f'{Strings.exception_resource_not_found}: {name}')