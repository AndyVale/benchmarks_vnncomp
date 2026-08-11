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
- 2026-08-11: Added `tests/test_generation.py` covering CLI normalization/delegation, dataframe filters, parameter bounds, repository path resolution, expected-result filtering, per-network sampling, and CSV output. Also corrected architecture list parsing and made instance-path resolution use the repository root constant.
- 2026-08-11: With `.venv` activated and `uv run pytest`, the first run found one incorrect test expectation involving an intentionally excluded `Add` node; corrected the fixture configuration. `uv` required a writable temporary cache because the default cache directory is restricted.
- 2026-08-11: Final command `source .venv/bin/activate && UV_CACHE_DIR=/tmp/benchmarks_vnncomp_uv_cache uv run pytest -q tests/test_generation.py` passed: 9 tests passed. Untracked Python bytecode generated during testing was removed. Existing uv project files (`pyproject.toml`, `uv.lock`, `.python-version`, and `main.py`) were preserved.
- 2026-08-11: Added `.gitignore` rules for Python bytecode/cache files and environment files, while allowing a potential `.env.example` template.
- 2026-08-11: Reproduced GUI startup with `python3 -m GUI_gen_instance.gen_instance_GUI`; fixed the missing `GITHUB_REPO` shared constant and imported it explicitly into the GUI controller.
- 2026-08-11: Diagnosed GUI startup failure caused by passing an output-path string to `get_network_tuples`, which now expects a configuration dictionary. Fixed the call and changed metadata-table loading to avoid scanning every `instances.csv` until generation is requested.
- 2026-08-11: Audited GUI update paths and found that every filter interaction reparsed `nns.csv`. Added a controller-level metadata cache; filter operations now use a deep copy of cached metadata, eliminating repeated disk I/O and CSV parsing while preserving filter isolation.
- 2026-08-11: Profiled startup: `gen_instances` import was about 0.18s, controller initialization about 0.003s, and metadata table preparation about 0.004s. The remaining synchronous cost is Tk widget/table construction during `BenchmarkScrollFrame` initialization. Deferred the initial table build with `after_idle`, allowing the main window to render before table widgets are created.
- 2026-08-11: Found the primary graphics bottleneck: four bundled `CTkScrollableDropdown` widgets eagerly created roughly 226 buttons each for ONNX node choices. Replaced them with native `CTkComboBox` widgets and replaced the unnecessary `CTkXYFrame` wrapper with `CTkScrollableFrame`. The GUI now consistently uses CustomTkinter and CTkTable only; PyQt6 was not introduced.
- 2026-08-11: Further profiling found tab and resize lag caused by `CTkTable` creating one `CTkButton` per cell and redrawing the entire widget tree during resize. Chose a full PyQt6 migration. Component mapping: `CTk` -> `QMainWindow`; `CTkFrame`/scrollable frames -> `QWidget` plus Qt layouts and scroll areas; `CTkCheckBox` -> `QCheckBox`; `CTkEntry`/`CTkComboBox` -> `QLineEdit`/`QComboBox`; `CTkButton` -> `QPushButton`; `CTkTabview` -> `QTabWidget`; `CTkTable` -> model-backed `QTableView`; `CTkToplevel` -> `QDialog`. No CustomTkinter or CTkTable components will remain active after migration.
- 2026-08-11: Completed the PyQt6 migration, removed the CustomTkinter dependency from `pyproject.toml`, removed the bundled `CTkScrollableDropdown` and `CTkXYFrame` components, and updated the README. The GUI now has one graphics stack only: PyQt6.
- 2026-08-11: Installed PyQt6 through `uv sync`, regenerated `uv.lock`, verified no CustomTkinter/CTkTable/CTkScrollableDropdown/CTkXYFrame references remain in active GUI code, and validated the Qt window can be constructed headlessly. Unit tests pass: 10 passed.
