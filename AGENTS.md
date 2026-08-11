# Agent Context

## Repository purpose

This repository organizes VNNCOMP benchmark submodules into convolutional, fully connected, and residual architectures. The benchmark directories contain networks, properties, and `instances.csv` files; refactoring work should rely on directory structure and metadata rather than inspecting instance contents.

## Refactoring objective

Keep shared instance-generation logic and constants in `gen_instances.py`. Provide separate thin adapters for the command-line interface and the GUI. Preserve the existing filtering and output behavior while removing the duplicated implementation in `GUI_gen_instance/definitions.py`.

## Current implementation notes

- `gen_instances.py` currently mixes reusable generation functions with CLI parser/setup code.
- Important constants are currently initialized only inside the `__main__` block, which makes importing the module unsafe.
- `GUI_gen_instance/definitions.py` duplicates most generation functions and has a result-filtering reference to the CLI global `arg_dict`.
- `GUI_gen_instance/logic.py` is the GUI controller and should delegate to `gen_instances.py`.
- GUI widget modules access the controller through `logic_instance`; preserve that interface during migration.

## Planned changes

1. Make `gen_instances.py` importable and centralize constants/shared operations.
2. Add `cli_gen_instances.py` for CLI execution.
3. Make GUI definitions a compatibility re-export and update GUI logic imports/calls.
4. Update `README.md` with CLI and GUI usage.
5. Verify imports, parser help, and shared filtering behavior without inspecting benchmark instance contents.

## Work log

- 2026-08-11: Inspected repository structure, root README, `gen_instances.py`, and GUI modules. No benchmark instance contents were inspected.
- 2026-08-11: Added this context file, moved shared constants to module scope, added `generate_instances`, made GUI definitions a compatibility re-export, added `cli_gen_instances.py`, and changed GUI imports to package-relative imports.
- 2026-08-11: Updated the root README with the CLI/GUI entry points and shared-logic architecture.
- 2026-08-11: Syntax compilation passed with `python3 -m py_compile`. Runtime import/help checks could not run because the environment lacks the `pandas` dependency. Generated untracked bytecode was removed; two pre-existing tracked GUI bytecode files were inadvertently removed during cleanup but could not be restored because this environment denies Git index-lock creation.
