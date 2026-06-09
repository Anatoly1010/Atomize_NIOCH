# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`Atomize_ITC` is the EPR-endstation variant of [Atomize](https://github.com/Anatoly1010/Atomize) — a modular instrument-control framework for spectrometers. It extends upstream Atomize with an "EPR Endstation Control" tab in the main window (`atomize/main/main.py`), Insys FM214x3GDA FPGA support (DAC / ADC / TTL pulser via ctypes against `libs/lib*.so`), and a set of dedicated control-center subprocesses (CW EPR, TR EPR, oscilloscopes, MW bridge, magnetic field, temperature, resonator tuning, RECT/AWG phasing).

Python is the scripting language. Experimental scripts are ordinary Python files that import device-module classes and call `general` functions to push data to the LivePlot-based GUI.

## Common commands

```powershell
# Install in editable mode (run from repo root). pyproject.toml requires Python >=3.10.
pip install -e .

# Optional extras (defined in pyproject.toml [project.optional-dependencies])
pip install -e .[serial,modbus,bots,math]

# Launch the main GUI
python -m atomize
# or via the installed entry point
atomize-itc

# Launch and immediately open an experimental script
python -m atomize path\to\script.py
```

There is no unit-test suite. The `Test Scripts` checkbox in the GUI runs a pre-flight syntax/import check by re-executing the script with `argv[1] == 'test'`; device modules and `general.message`/`general.wait`/etc. branch on `self.test_flag == 'test'` to skip real I/O. To smoke-test a single script in test mode without the GUI: `python path\to\script.py test`. Example/demo scripts live in `atomize/script_examples/` (not `atomize/tests/` — that path in the upstream README is stale here).

## Big-picture architecture

### Multi-process model

The GUI is **one Qt process that spawns many `QProcess` children**, not a monolithic event loop:

- `atomize/main/main.py:MainExtended` — extends the upstream `MainWindow` with a third tab ("EPR Endstation Control"). Each control-center button (`start_tr_control`, `start_osc_control`, `start_cw`, `start_field_control`, `start_temp_control`, `start_mw_control`, `start_tune_preset`, `start_rect_phasing`, `start_awg_phasing`, …) launches a script under `atomize/control_center/` via a dedicated `QProcess` (`process_tr`, `process_osc`, etc.).
- `start_experiment` in `main.py` spawns the user's experimental script in `self.process_python`.
- Children communicate **upward** by writing `print "..."` to stdout; the parent's `handle_output*` parses lines prefixed with `print `, `before `, `closing `, or `ret = 0` and routes them to the in-app log (`text_errors`). The `before ` / `ret = 0` sentinels exist specifically to suppress Insys FPGA driver chatter.
- The parent communicates **downward** to the active script by writing JSON-ish responses to its stdin when the child prints `create_file_dialog` / `open_file_dialog` — this is how scripts trigger native file pickers.

When editing anything in `atomize/main/main.py` or the control-center scripts, remember every `general.message(...)` call becomes a `print` over a pipe — don't replace it with a normal `print` or it'll be eaten by the routing logic.

### LivePlot data path

Plotting is a second IPC layer parallel to stdout:

- The main window starts a `QLocalServer` named `LivePlot` (`atomize/main/main_window.py`).
- Each child script imports `atomize.general_modules.general_functions`, which instantiates a `LivePlotClient` (`atomize/main/client.py`). The client connects to the local socket, allocates a `QSharedMemory` block, and sends NumPy array payloads via shared memory plus a JSON metadata header over the socket.
- The main window's `accept` / `read_from` callbacks attach to the same shared memory and forward to the pyqtgraph DockArea.

This is why `general.plot_1d(...)` only works when called from a script launched **through** the main window — outside of that, the `LivePlotClient` constructor raises `EnvironmentError("Couldn't find LivePlotter instance")`.

### Device module convention

Every device gets a parallel pair:

- `atomize/device_modules/<Device>.py` — class named the same as the file, instantiated by experimental scripts (`import atomize.device_modules.Lakeshore_335 as ls; ls335 = ls.Lakeshore_335()`).
- `atomize/device_modules/config/<Device>_config.ini` — sectioned config (`DEFAULT`, `GPIB`, `SERIAL`, `MODBUS`, `ETHERNET`, `SPECIFIC`). The `DEFAULT.type` field (`gpib` / `rs232` / `ethernet` / `modbus`) picks which section is used at connect time.

`atomize/device_modules/config/config_utils.py` has the shared `read_conf_util` / `read_specific_parameters` helpers that every device module calls. Transport layers: pyvisa (GPIB/RS-232/Ethernet/VXI-11), pyserial directly, minimalmodbus, raw sockets for TCP/UDP, and **ctypes** for vendor binaries — `libs/libNvsbLib.so`, `libs/libConfigGIM.so`, `libs/GIM.so`, `libs/libbambpex.so` (Insys FPGA) and `atomize/general_modules/libspinapi.so` (SpinCore Pulse Blaster).

When adding a new device, model after an existing one of the same transport class (e.g. copy `Lakeshore_335.py` for a new GPIB/RS-232 device) and add its config file. The class name **must** match the module filename.

### Config-file lifecycle (important gotcha)

`atomize/main/local_config.py:copy_config` runs on every startup and copies:
- `atomize/config.ini` → `<user_config_dir>/atomize-py/main_config.ini`
- `atomize/device_modules/config/*` → `<user_config_dir>/atomize-py/device_config/`

…but **only if** the user config directory is missing or empty. After first launch, device modules read from the user-config copy (via `lconf.load_config_device()`), not the repo copy. Editing `atomize/device_modules/config/Foo_config.ini` in-repo will **not** affect a running install; either edit the file under `user_config_dir("atomize-py")/device_config/` or wipe that directory to force a re-copy. On Windows this is typically `%LOCALAPPDATA%\atomize-py\atomize-py\` (resolved by `platformdirs`).

`atomize/main/main_window.py` also `os.chdir`'s into `libs/` early in startup, so any relative paths after that point are resolved against `libs/`. The `libs/status` file and `*.param` files (`field.param`, `bridge.param`, `digitizer*.param`, `correction.param`) are runtime IPC files between control-center widgets and other processes — they're git-ignored and intentionally mutated at runtime.

### Pulse-EPR experiment presets

`atomize/control_center/experiments/*.phase` and `*.phase_awg` are saved phase-cycle/pulse-sequence presets consumed by the phasing/tune control scripts (`phasing_insys.py`, `awg_phasing_insys.py`, `tune_preset.py`, etc.). The `_insys` suffix in `atomize/control_center/other_versions/` marks Insys-FPGA-specific variants; non-suffixed siblings target Spectrum / oscilloscope hardware.

### General script-side API

Experimental scripts almost always start with:

```python
import atomize.general_modules.general_functions as general
import atomize.general_modules.csv_opener_saver as openfile
```

- `general.message(...)`, `general.message_test(...)` — print to the main-window log (and only in non-test / only-in-test runs respectively).
- `general.wait('10 ms')` — string-with-unit time API used everywhere (`ks/s/ms/us/ns/ps`). Time arguments to device functions follow the same convention.
- `general.plot_1d`, `general.plot_2d` — push to LivePlot.
- `general.to_infinity()` — generator for `Stop`-button-aware infinite loops.
- `general.bot_message(...)` — Telegram (requires token+chat-id in `main_config.ini`).
- `atomize.general_modules.returned_thread.rThread` — `threading.Thread` subclass whose `join()` returns the target's return value; this is the project's standard concurrency primitive (see `atomize/documentation/concurrency.md`).
- `openfile.Saver_Opener()` — CSV I/O with header support and Tk-style file dialogs.

### Documentation

The per-instrument function reference is markdown in `atomize/documentation/` (rendered as the Jekyll site at `anatoly1010.github.io/atomize_docs`). When changing a device module's public API, also touch the matching `*.md` there.

## Conventions worth knowing

- Time strings everywhere use the `"<float> <unit>"` form (`'10 ms'`, `'1.5 us'`). Never pass bare floats.
- Module class name == filename. Breaking that breaks the `import X as foo; foo.X()` convention used in every example.
- `test_flag = sys.argv[1]` is the standard way modules detect test mode. Preserve the `argv[1] == 'test'` branch when adding code that touches hardware.
- Don't introduce `print()` statements in scripts launched by the GUI — use `general.message(...)`. Bare `print` to stdout is interpreted by the parent's line-parser and either dropped or shown raw.
- `.param`, `.csv` temp files, `libs/status`, `libs/exam_adc.ini`, `libs/exam_edac.ini`, and `Metrolab_PT2025*` are git-ignored on purpose (see `.gitignore`). Don't commit local edits to them.
