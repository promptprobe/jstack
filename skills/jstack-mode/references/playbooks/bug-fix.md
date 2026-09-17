# Bug fix

Capture the failing input, expected output and actual result. Reproduce with the
smallest reliable test or runtime sequence. If reproduction fails, label the
diagnosis tentative; preserve what was tried instead of asserting a root cause.

Trace the incorrect state to its producer. Add a regression check when it will
catch a future recurrence, observe it failing, then fix that cause. Check the
original reproduction and adjacent boundary cases. A workaround is acceptable
when required by scope, but name it and its remaining failure modes. Stop repeated
guess-and-retry cycles at the selected budget.
