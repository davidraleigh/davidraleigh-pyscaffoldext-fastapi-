from typing import List

from pathlib import Path
from pyscaffold.actions import Action, ActionParams, ScaffoldOpts, Structure
from pyscaffold.extensions import Extension

from pyscaffold.operations import no_overwrite
from pyscaffold.structure import merge, reject
from pyscaffold.templates import get_template

from pyscaffoldext import templates


class Fastapi(Extension):
    """
    This class serves as the skeleton for your new PyScaffold Extension. Refer
    to the official documentation to discover how to implement a PyScaffold
    extension - https://pyscaffold.org/en/latest/extensions.html
    """

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension. See :obj:`pyscaffold.extension.Extension.activate`."""
        actions = self.register(actions, add_files)
        actions = self.register(actions, remove_files, after="define_structure")
        # return self.register(actions,  custom_setup_cfg, after="define_structure")
        return actions


def remove_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Remove all skeleton files from structure

    Args:
        struct: project representation as (possibly) nested :obj:`dict`.
        opts: given options, see :obj:`create_project` for an extensive list.

    Returns:
        Updated project representation and options
    """
    # Namespace is not yet applied so deleting from package is enough
    # print(struct)
    # print(opts)
    src = Path("src")
    struct = reject(struct, src / opts["package"] / "skeleton.py")
    struct = reject(struct, "tests/test_skeleton.py")
    return struct, opts


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add custom extension files. See :obj:`pyscaffold.actions.Action`"""
    opts['requirements'] = ['pydantic']

    main_template = get_template("main", relative_to=templates.__name__)
    init_template = get_template("init", relative_to=templates.__name__).template
    conf_template = get_template("conf", relative_to=templates.__name__).template
    core_template = get_template("core", relative_to=templates.__name__)

    api_http_template = get_template("api_http", relative_to=templates.__name__)
    api_models_template = get_template("api_models", relative_to=templates.__name__).template

    db_alembic_ini_template = get_template("db_alembic_ini", relative_to=templates.__name__).template
    db_migrations_env_template = get_template("db_migrations_env", relative_to=templates.__name__)
    db_script_py_mako_template = get_template("db_script_py_mako", relative_to=templates.__name__).template
    db_models_template = get_template("db_models", relative_to=templates.__name__)

    test_template = get_template("test", relative_to=templates.__name__)

    files: Structure = {
        "src": {
            opts["package"]: {
                "api": {
                    "http.py": (api_http_template, no_overwrite()),
                    "models.py": (api_models_template, no_overwrite())
                },
                "db": {
                    "migrations": {
                        "env.py": (db_migrations_env_template, no_overwrite()),
                        "scripts.py.mako": (db_script_py_mako_template, no_overwrite()),
                        "__init__.py": ""
                    },
                    "models.py": (db_models_template, no_overwrite()),
                    "alembic.ini": (db_alembic_ini_template, no_overwrite()),
                    "__init__.py": ""
                },
                "__init__.py": (init_template, no_overwrite()),
                "__main__.py": (main_template, no_overwrite()),
                "conf.py": (conf_template, no_overwrite()),
                "core.py": (core_template, no_overwrite()),
            }
        },
        "tests": {"test_config.py": (test_template, no_overwrite())},
    }

    return merge(struct, files), opts


def custom_setup_cfg(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    from configupdater import ConfigUpdater
    from pyscaffold.templates import add_pyscaffold
    from pyscaffold import dependencies as deps

    template = get_template("setup_cfg")
    cfg_str = template.substitute(opts)
    updater = ConfigUpdater()
    updater.read_string(cfg_str)
    requirements = deps.add(deps.RUNTIME, opts.get("requirements", []))
    print(requirements)
    updater["options"]["install_requires"].set_values(requirements)

    # fill [pyscaffold] section used for later updates
    add_pyscaffold(updater, opts)
    pyscaffold = updater["pyscaffold"]
    pyscaffold["version"].add_after.option("package", opts["package"])

    struct['setup.cfg'] = lambda a: str(updater)

    return struct, opts
