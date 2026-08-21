import tomllib

from core.paths import get_backend_root


def get_app_version() -> str:
    pyproject_file = get_backend_root() / "pyproject.toml"

    with pyproject_file.open("rb") as f:
        pyproject = tomllib.load(f)

    return pyproject["project"]["version"]
