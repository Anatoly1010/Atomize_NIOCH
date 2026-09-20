# Phasing reference curves

Ported from Atomize_ITC to both `phasing.py` and `awg_phasing.py`.
The **T** button sits 4 px before the Repetition Rate spinbox, matching the
link-reset button spacing. Click once during a running preview to freeze the
current Dig I/Q and enabled FFT curves; click again to clear them. References
use the displayed colours at 30% opacity and stay behind the new data.

The reference and checked state survive preview stop/restart in the same
phasing window. Clearing remains available while stopped. Preflight and full
experiments cannot create a capture. The Live Mode editing checkbox does not
control Track, and the existing hardware acquisition and averaging are unchanged.

FFT can capture either one magnitude curve or both phase-corrected components.
Changing Phase Correction or toggling Live FFT clears only the FFT reference.
References retain their original x/y data, including across changes in record
length, time origin, and sample spacing. Auto range includes both curves.
Log X/Log Y affect presentation only; returning to linear restores all raw values,
including zero and negative samples hidden by logarithmic axes.

References are held in memory, separate from acquisition/export data. Closing
the phasing window, deleting/clearing the plot, or a different tool taking over
that plot removes them. Dig and FFT capture the currently displayed frames,
which may come from adjacent acquisitions. If no current data exists yet, the
log requests an off/on retry after curves arrive; T remains checked.

## Port review and validation

The GUI sends Track commands through the existing control-center output channel.
Plot frames identify their worker and parent process to reject stale data and
retain references across a preview worker restart. The plotting backend matches
ITC, including independent copied axes and full-data auto-range bounds.

- 75 focused offscreen tests passed for this fork.
- Both phasing windows were checked at widths 1720 and 2300: T-to-spinbox gap
  is 4 px and the Repetition Rate and Field inputs remain aligned.
- Hardware acquisition and Windows execution were not run.

NIOCH preserves its manual I/Q phase-inversion display. Capture freezes the
currently corrected values without applying the correction a second time.
Its hardware acquisition workers are unchanged.

## Auto Phase and Auto Window preflight guard

Both phasing tools reject Auto Phase and Auto Window requests while the
throwaway preflight worker is running. After preflight finishes, both controls
work normally in the acquisition preview. The existing experiment and
Phase Correction restrictions are unchanged. Auto Window still sends its
width in nanoseconds, and Auto Phase updates Zero Order and sends radians
back to the worker. No acquisition calculations or worker messages changed.

Validation: 50 auto-control and Stop checks passed, including the real Qt
Zero Order spinbox feedback path. No hardware acquisition was run.
