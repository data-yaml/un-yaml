import logging
from pathlib import Path
from tempfile import TemporaryDirectory


from .un_attr import UnAttr


class UnDir(UnAttr):
    ARG_DIR = "dir"

    def __init__(self, attrs: dict):
        """
        Base class to set and manage local sync directory
        (starting with a temporary one).

        >>> import shutil
        >>> ud = UnDir({})
        >>> hasattr(ud, "dir_path")
        True
        >>> ud.dir_path.is_dir()
        True
        >>> u2 = UnDir({UnAttr.K_ID: "foo"})
        >>> str(u2.dir_path)
        'foo'
        >>> u2.dir_path.exists()
        False
        >>> d2 = u2.dir()
        >>> d2.is_dir()
        True
        >>> str(d2).endswith("foo")
        True
        >>> shutil.rmtree(d2)
        """
        super().__init__(attrs)
        default_dir: str = self.attrs.get(UnAttr.K_ID, False)
        self.dir_path = Path(default_dir) if default_dir else self.make_temp_dir()

    def make_temp_dir(self) -> Path:
        self.temp_dir: TemporaryDirectory = TemporaryDirectory(
            ignore_cleanup_errors=True
        )
        return Path(self.temp_dir.name)

    def __del__(self):
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    def dir(self, *paths: str) -> Path:
        """
        Return a path relative to the local sync directory.

        >>> import shutil
        >>> ud = UnDir({})
        >>> sub = ud.dir("c", "d")
        >>> sub.exists()
        True
        >>> sub.is_dir()
        True
        >>> str(sub.as_posix()).endswith("/c/d")
        True
        >>> base = ud.dir()
        >>> sub2 = base / "c" / "d"
        >>> sub2 == sub
        True
        >>> shutil.rmtree(sub)
        >>> shutil.rmtree(base)
        """
        p = self.dir_path
        for path in paths:
            p = p / path

        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    def local_files(self) -> list[Path]:
        """
        Return a list of all files in the local sync directory.
        """
        return [f for f in self.dir().rglob("*") if f.is_file()]

    def check_dir(self, dir_str: str | None = None) -> Path:
        """
        Updated and return dir, if dir_str valid (create if necessary)
        Expand if contains attrs.

        Args:
            dir_str (str): String for local_dir (may contain attrs)

        Returns:
            Path: self.dir_path (gauranteed to exist)

        Raises:
            ValueError: If dir_str exists and is not a directory

        """
        if not dir_str or len(dir_str) == 0:
            return self.dir_path

        dir_var = dir_str.format(**self.attrs)
        logging.debug(f"check_dir: {dir_var} <= {self.attrs}")
        local_path = Path(dir_var).resolve()

        if not local_path.exists():
            logging.warning(f"Path does not exist: {local_path}")
            local_path.mkdir(parents=True, exist_ok=True)
        elif not local_path.is_dir():
            raise ValueError(f"Path is not a directory: {local_path}")
        self.dir_path = local_path
        return self.dir_path

    def check_dir_arg(self, args: dict):
        """
        Check for UnDir.ARG_DIR in args and update self.dir_path if valid.
        """
        local_dir = args.get(UnDir.ARG_DIR)
        return self.check_dir(local_dir)

    def write_text(self, text: str, filename: str, *paths: str) -> Path:
        """
        Write text to file in local sync directory.
        """
        p = self.dir(*paths) / filename
        p.write_text(text)
        return p
