"""Regression checks for NIOCH's phase-registry race and save snapshots."""
import ast
import inspect
import multiprocessing as mp
import os
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(os.environ.get('ATOMIZE_NIOCH_ROOT', Path(__file__).resolve().parents[1]))
ROOT_Q = Path(os.environ.get('ATOMIZE_NIOCH_Q_ROOT', ROOT.parent / 'Atomize_NIOCH_Q'))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atomize.general_modules import csv_opener_saver_invert as saver_mod
from atomize.general_modules import inversion_param as inv_par


def _registry_writer(registry, operation, entered, done, fail=False, ready=None, proceed=None):
    """Pause after reading so a second process must wait for the registry lock."""
    from atomize.general_modules import inversion_param as registry_mod

    registry_mod.path = lambda: registry
    original_read, original_write = registry_mod.read, registry_mod._write
    first = True

    def delayed_read():
        nonlocal first
        value = original_read()
        if first:
            first = False
            entered.set()
            if proceed is not None and not proceed.wait(10):
                raise RuntimeError('registry writer was not released')
        return value

    registry_mod.read = delayed_read
    if fail:
        registry_mod._write = lambda data: (_ for _ in ()).throw(OSError('planned write failure'))
    if ready is not None:
        ready.set()
    try:
        if operation == 'phase':
            registry_mod.set_phase('plot', 'curve', 90)
        elif operation == 'freq':
            registry_mod.set_detection_freq(-77)
        else:
            registry_mod.reset()
    except OSError:
        done.put('expected-error')
    else:
        done.put('ok')
    finally:
        registry_mod.read, registry_mod._write = original_read, original_write


@pytest.fixture(autouse=True)
def isolated_registry(monkeypatch, tmp_path):
    monkeypatch.setattr(inv_par, 'path', lambda: str(tmp_path / 'inversion.param'))
    monkeypatch.setattr(inv_par, '_last_freq', None)


def fresh_saver():
    result = saver_mod.Saver_Opener.__new__(saver_mod.Saver_Opener)
    result.test_flag = 'None'
    result.save_cancelled = False
    return result


def rotated(data, phase):
    result = data.copy()
    iq = (data[:, 1] + 1j * data[:, 2]) * np.exp(1j * np.deg2rad(phase))
    result[:, 1], result[:, 2] = iq.real, iq.imag
    return result


def test_real_multiprocess_phase_and_frequency_writes_preserve_both(tmp_path):
    """The second writer starts while the first has read old state."""
    registry = str(tmp_path / 'shared_registry')
    context = mp.get_context('spawn')
    entered, done = context.Event(), context.Queue()
    release_phase = context.Event()
    phase = context.Process(target=_registry_writer,
                            args=(registry, 'phase', entered, done),
                            kwargs={'proceed': release_phase})
    freq_entered, freq_ready = context.Event(), context.Event()
    freq = context.Process(target=_registry_writer,
                           args=(registry, 'freq', freq_entered, done),
                           kwargs={'ready': freq_ready})
    try:
        phase.start()
        assert entered.wait(3), 'phase writer never reached read-modify-write'
        freq.start()
        assert freq_ready.wait(5)
        assert not freq_entered.wait(0.3), 'second writer read while the first held the lock'
        release_phase.set()
        assert done.get(timeout=5) == 'ok'
        assert done.get(timeout=5) == 'ok'
        phase.join(3)
        freq.join(3)
        assert phase.exitcode == freq.exitcode == 0
    finally:
        release_phase.set()
        for process in (phase, freq):
            if process.is_alive():
                process.terminate()
            if process.pid is not None:
                process.join(3)
    inv_par.path = lambda: registry
    assert inv_par.applied_phase('plot', 'curve') == 90
    assert inv_par.detection_freq() == -77


def test_advisory_lock_releases_when_registry_write_raises(tmp_path):
    registry = str(tmp_path / 'shared_registry')
    context = mp.get_context('spawn')
    entered, done = context.Event(), context.Queue()
    broken = context.Process(target=_registry_writer,
                             args=(registry, 'phase', entered, done, True))
    succeeding_entered = context.Event()
    succeeding = context.Process(target=_registry_writer,
                                args=(registry, 'freq', succeeding_entered, done))
    try:
        broken.start()
        assert entered.wait(3)
        assert done.get(timeout=5) == 'expected-error'
        broken.join(3)
        assert broken.exitcode == 0
        # A separate process must acquire the same stable *.lock afterward.
        succeeding.start()
        assert done.get(timeout=5) == 'ok'
        succeeding.join(3)
        assert succeeding.exitcode == 0
    finally:
        for process in (broken, succeeding):
            if process.is_alive():
                process.terminate()
            if process.pid is not None:
                process.join(3)
    assert Path(registry + '.lock').exists()


@pytest.mark.parametrize('extension', ['.csv', '.h5'])
def test_explicit_saver_phase_bypasses_registry_and_default_stays_dynamic(tmp_path, extension):
    if extension == '.h5':
        h5py = pytest.importorskip('h5py')
    signature = inspect.signature(saver_mod.Saver_Opener.save_data)
    parameters = list(signature.parameters)
    assert parameters[-1] == 'phase'
    assert signature.parameters['phase'].default is None
    data = np.array([[0., 1., 2.], [1., -3., 4.]])
    inv_par.set_phase('plot', 'curve', 90)
    explicit = tmp_path / ('explicit' + extension)
    fresh_saver().save_data(explicit, data, header='explicit', plot='plot', label='curve',
                            phase=180, axes=(np.arange(2), np.arange(2)),
                            axes_units=('s', 'G'))
    if extension == '.h5':
        with h5py.File(explicit) as handle:
            actual = handle['I'][...]
    else:
        actual = np.loadtxt(explicit, delimiter=',')
    np.testing.assert_allclose(actual, rotated(data, 180), atol=2e-6)
    inv_par.set_phase('plot', 'curve', -90)
    dynamic = tmp_path / ('dynamic' + extension)
    fresh_saver().save_data(dynamic, data, plot='plot', label='curve',
                            axes=(np.arange(2), np.arange(2)), axes_units=('s', 'G'))
    if extension == '.h5':
        with h5py.File(dynamic) as handle:
            actual = handle['I'][...]
    else:
        actual = np.loadtxt(dynamic, delimiter=',')
    np.testing.assert_allclose(actual, rotated(data, -90), atol=2e-6)


def _method(tree, name):
    worker = next(node for node in tree.body
                  if isinstance(node, ast.ClassDef) and node.name == 'Worker')
    return next(node for node in worker.body
                if isinstance(node, ast.FunctionDef) and node.name == name)


def _save_branch(method):
    branch = next(
        node for node in ast.walk(method)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == 'script_test'
        and any('file_handler.save_data' in ast.unparse(statement) for statement in node.orelse)
    )
    return compile(ast.Module(body=branch.orelse, type_ignores=[]),
                   '<actual AWG save branch>', 'exec')


class _FileDialog:
    def __init__(self, filename):
        self.filename = filename

    def send(self, message):
        pass

    def poll(self):
        return True

    def recv(self):
        return 'FL' + self.filename


class _ChangingRegistry:
    def __init__(self, first_phase):
        self.first_phase = first_phase
        self.lookups = 0

    def applied_phase(self, plot, curve):
        self.lookups += 1
        return self.first_phase if self.lookups == 1 else -37


def _run_actual_save_branch(method_name, filename):
    tree = ast.parse((ROOT / 'atomize/control_center/awg_phasing.py').read_text())
    raw = np.arange(24., dtype=float).reshape(2, 3, 4) - 9
    registry = _ChangingRegistry(144)
    namespace = dict(
        conn=_FileDialog(str(filename)),
        file_handler=fresh_saver(),
        np=np,
        os=os,
        general=type('General', (), {'wait': staticmethod(lambda value: None)}),
        inv_par=registry,
        self=type('Worker', (), {'save_hdf5': 1})(),
        data=raw,
        data_x=raw[0].sum(axis=0),
        data_y=raw[1].sum(axis=0),
        x_axis=np.arange(4),
        x_axis_plot=np.arange(4),
        points_window=3,
        dec_calc=.4,
        iq_cor=1,
        save2d=1,
        header='raw',
        header2='integrated',
        EXP_NAME='experiment',
        curve_name='curve',
        receiver_level=None,
        save_each=True,
        cycle_snapshots=[raw.copy(), raw * 2],
        iq_freq=-100,
        zp=0,
        first_order=0,
        sec_order=0,
        dig=type('Digitizer', (), {
            'digitizer_demodulate': staticmethod(
                lambda i, q, *args, **kwargs: (i.sum(axis=0), q.sum(axis=0)))
        })(),
    )
    exec(_save_branch(_method(tree, method_name)), namespace)
    return namespace, raw, registry


@pytest.mark.parametrize('method_name', ['exp', 'exp_eseem', 'exp_field', 'exp_log', 'exp_amplitude'])
def test_actual_awg_save_blocks_use_one_phase_snapshot(method_name, tmp_path):
    h5py = pytest.importorskip('h5py')
    filename = tmp_path / f'{method_name}.csv'
    namespace, raw, registry = _run_actual_save_branch(method_name, filename)
    assert registry.lookups == 1
    expected = rotated(np.c_[namespace['x_axis_plot'], namespace['data_x'], namespace['data_y']], 144)
    np.testing.assert_allclose(np.loadtxt(filename, delimiter=','), expected, atol=2e-5)
    with h5py.File(tmp_path / f'{method_name}_2d.h5') as handle:
        np.testing.assert_array_equal(handle['I'][...], raw[0].T)
        np.testing.assert_array_equal(handle['Q'][...], raw[1].T)
    if method_name == 'exp_eseem':
        for index, multiplier in ((0, 1), (1, 3)):
            cycle = np.loadtxt(tmp_path / f'{method_name}_cycle{index}.csv', delimiter=',')
            input_data = np.c_[namespace['x_axis_plot'],
                               namespace['data_x'] * multiplier,
                               namespace['data_y'] * multiplier]
            np.testing.assert_allclose(cycle, rotated(input_data, 144), atol=2e-5)


def _exercise_add_new_plot(root, module_name):
    source = (root / 'atomize/main' / module_name).read_text()
    tree = ast.parse(source)
    cls_name = 'MainWindow' if module_name == 'main_window.py' else 'MainExtended'
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == cls_name)
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'add_new_plot')
    assert [arg.arg for arg in method.args.args][-1] == 'select'
    assert isinstance(method.args.defaults[-1], ast.Constant) and method.args.defaults[-1].value is True
    widgets = type('Widgets', (), {'get_widget': staticmethod(lambda rank, name: (rank, name))})
    namespace = {'widgets': widgets, 'widgets_invert': widgets}
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<shared add_new_plot>', 'exec'), namespace)
    add_new_plot = namespace['add_new_plot']

    class Names(dict):
        def __init__(self):
            super().__init__()
            self.selected = []

        def select_plot(self, name):
            self.selected.append(name)

    class Window:
        def __init__(self):
            self.namelist = Names()
            self.plots = []

        def add_plot(self, value):
            self.plots.append(value)
    window = Window()
    assert add_new_plot(window, 1, 'chosen', True) == (1, 'chosen')
    assert window.namelist.selected == ['chosen']
    add_new_plot(window, 2, 'quiet', False)
    assert window.namelist.selected == ['chosen']


def test_nioch_add_new_plot_honors_select():
    _exercise_add_new_plot(ROOT, 'main.py')


def test_shared_add_new_plot_honors_select_and_nioch_q_uses_it():
    if not ROOT_Q.is_dir():
        pytest.skip('NIOCH_Q sibling repository is unavailable')
    _exercise_add_new_plot(ROOT_Q, 'main_window.py')
    nioch_q = ast.parse((ROOT_Q / 'atomize/main/main.py').read_text())
    extended = next(node for node in nioch_q.body if isinstance(node, ast.ClassDef) and node.name == 'MainExtended')
    assert any(isinstance(base, ast.Name) and base.id == 'MainWindow' for base in extended.bases)
    assert not any(isinstance(node, ast.FunctionDef) and node.name == 'add_new_plot' for node in extended.body)
