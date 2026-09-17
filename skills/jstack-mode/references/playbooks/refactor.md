# Refactor

Name the behavior that must remain invariant and the structural problem being
removed. Capture current behavior with existing tests or a small characterization
fixture. Inventory callers at the boundary being changed.

Move one responsibility at a time where useful, keeping contracts stable unless a
contract migration is explicitly in scope. Run the same checks before and after;
review removed code and remaining callers. Do not report performance gains or
behavior improvements without separate measurements. Explain the simpler final
structure and any migration steps.
