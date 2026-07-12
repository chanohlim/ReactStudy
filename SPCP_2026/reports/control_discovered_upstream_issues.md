# Control-Phase Discovered Upstream Issues

No focal resolver changes were made. Focal stayed at 0.8833.

The current checkout did not contain the target-candidate resolver described in the task context, so the stable target resolver structure was carried forward in `harness.py` before measuring `control_before`. After the control work, target stayed at 0.8000 and target@correct-focal stayed at the expected 0.9057-level subset.

Remaining control misses were not used to add task-specific focal or target exceptions.
