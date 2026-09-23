# Phasing reference curves

Ported from Atomize_ITC to both `phasing.py` and `awg_phasing.py`.
The **T** and **×** buttons sit between the Repetition Rate label and its
spinbox. During a running preview, click T to freeze the current Dig I/Q and
enabled FFT curves; each click captures anew and replaces the previous
references. × clears them at any time, including while stopped. References are
drawn behind the new data at 70% opacity in fixed colours, cyan for the first
curve and magenta for the second, with the source curve's line width and a
legend entry such as `ch ref` or `FFT ref`.

References survive preview stop/restart in the same phasing window. T is
disabled while the preview is stopped, during preflight, and during full
experiments. The Live Mode editing checkbox does not control T, and the
existing hardware acquisition and averaging are unchanged.

FFT can capture either one magnitude curve or both phase-corrected components.
Changing Phase Correction or toggling Live FFT clears only the FFT reference.
References retain their original x/y data, including across changes in record
length, time origin, and sample spacing. Auto range includes both curves.
Log X/Log Y affect presentation only; returning to linear restores all raw values,
including zero and negative samples hidden by logarithmic axes.

References are held in memory, separate from acquisition/export data. Closing
the phasing window, deleting/clearing the plot, or a different tool taking over
that plot removes them. Dig and FFT capture the currently displayed frames,
which may come from adjacent acquisitions. If any requested plot has no current
curves yet (for example FFT was just enabled), the capture changes nothing:
existing references stay and the main log names the missing plot. Click T again
once the curves appear.

## Port review and validation

The GUI sends Track commands through the existing control-center output channel.
Plot frames identify their worker and parent process to reject stale data and
retain references across a preview worker restart. The plotting backend matches
ITC, including independent copied axes and full-data auto-range bounds.

- 75 focused offscreen tests passed for this fork.
- Both phasing windows were checked at widths 1720 and 2300: button-to-spinbox
  gap is 4 px and the Repetition Rate and Field inputs remain aligned.
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

## One-click capture and clear

Ported from Atomize_ITC. T no longer toggles, so it cannot stay lit with no
references. A capture checks every requested plot before replacing the old
references. The × glyph on the clear and link-reset buttons is centred by its
ink rather than its text line.

Validation: the full test suite passed (115 passed), including one-click
replacement, failed captures keeping old references, reference colours, opacity,
width and legend names, and T/× enabled states. Offscreen builds of both phasing
windows confirmed the Repetition Rate spinbox keeps its position, aligned with
the Field input below. No hardware acquisition was run.
