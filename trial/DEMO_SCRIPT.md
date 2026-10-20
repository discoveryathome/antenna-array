# A 35-second public demonstration

Use `figures/contributor-progress.gif` or its four numbered PNG frames. The frames are actual evaluated designs. Keep the ideal-model label visible.

**0–8 seconds, coherent steering.** “These sixteen antennas all send the same signal strength. Changing their relative timing changes where their waves add together and where they cancel.” Point to the forward main beam and the two shaded quiet sectors. This is a cut through an ideal radiation pattern, not a map of measured coverage.

**8–16 seconds, starting pilot.** “The starter design already makes those chosen directions quieter while keeping most of the useful forward signal.” Label this explicitly as work that existed before the contributor trial. Point out that other directions can get brighter: cancellation redistributes the pattern.

**16–26 seconds, paired moves then refinement.** “A contributor changes the phase settings together and handles their rounding more carefully. That earns another half-decibel on this case—about eleven percent less power in the limiting sidelobe relative to the forward signal.” Show the score changing from −13.130 to −13.636 dB. This is incremental improvement, not an entirely new antenna or an eleven-percent increase in radio range.

**26–35 seconds, robustness figure.** “A design also has to survive imperfect calibration. The next contribution is a mathematical gain margin that covers all errors inside a stated small error box.” Show `figures/robustness.png`. Explain that the guarantee is for coherent gain in the model, and preserving that margin costs some nominal suppression.

The honest invitation is to improve and verify designs under real constraints. Do not imply a new physics discovery, measured hardware performance, a unique three-dimensional pencil beam, or that every half-hour session will produce the same improvement. A radio engineer still needs to define and validate the physical model for a real application.
