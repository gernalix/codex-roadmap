PROMPT_ID: 128463

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Fix Places check-in disambiguation so being inside more than one saved Place/geofence always requires an explicit user choice.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInPolicy.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInCapsule.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/LuoghiHomeViewModel.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/home/HomeScreen.kt`

Open `PlaceRepository.kt` only if a failing persistence test shows the selected ID is not saved correctly; do not inspect map/geofence/location code otherwise. If a prior task renamed a listed symbol, use one targeted symbol search only.

## Known decisive evidence
Current `CheckInPolicy.choosePlace()` already builds all in-radius candidates and already has an `Ambiguous` result, but when multiple candidates exist it only returns `Ambiguous` if the first two center distances differ by at most 10 m; otherwise it silently chooses the nearest. Geofence overlap is determined by each Place radius, not by near-equal center distance, so this can auto-check-in to the wrong Place while the user is simultaneously inside multiple saved Places.

## Requirements
- zero candidates: preserve current Unknown behavior;
- exactly one candidate: preserve automatic Match;
- **two or more candidates: always return/use the existing Ambiguous selection flow** containing the matching candidates; never auto-pick solely because one center is >10 m nearer;
- record only the selected canonical Place ID;
- cancellation creates no check-in;
- preserve efficient current GPS/location behavior; no new polling/geofence redesign.

If the current UI artificially caps choices below the actual realistic overlap set, adjust only as necessary so a matching Place cannot silently disappear; do not redesign the dialog.

## Acceptance
Targeted tests cover 0/1/2+ candidates, including two overlapping Places whose center-distance difference is >10 m, and cancellation/selected persistence. Focused device/emulator check only if needed to prove the existing selector wiring.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, policy change, tests, device check if any, commit SHA.
