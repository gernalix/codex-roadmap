PROMPT_ID: 653920

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Add manual historical check-in/out to every saved Place for visits that cannot be reconstructed from current GPS.

## Exact starting files — verified on PersonalHub/main
Read these in one grouped pass only:
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/HistoryModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/visits/VisitMapper.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/visits/VisitUiModel.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MainActivity.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/place/PlaceDetailScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/history/HistoryDialogs.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/history/HistoryScreen.kt`

Open `LuoghiHomeViewModel.kt` only if the existing navigation/mutation callback is needed to wire the action. Do not inspect GPS/geofence/map code. If an earlier task renamed a listed symbol, resolve it with one targeted search only.

## Requirements
- Add a clear action on each Place to create a manual historical visit.
- Let the user specify check-in and check-out date/time; support an open visit only if the current canonical model safely supports it.
- Persist the same canonical Place ID and the same event/session history model used by automatic visits; no parallel history table/system.
- Reuse existing overlap/temporal validation where possible: reject checkout-before-checkin, conflicting/overlapping records and accidental duplicates according to current domain rules.
- Preserve a cheap provenance/source value for manual creation if the existing event model supports it; do not fork downstream queries by provenance.
- Manual visits must appear in the same history/stats/query paths as automatic visits and survive reopen.

## Scope / safety
No GPS/geofence behavior change, route inference or unrelated Places UI redesign. Minimal diff and targeted tests only.

## Acceptance
Tests cover valid historical interval, boundary/overlap validation, duplicate/conflict prevention, canonical history visibility and reopen persistence. Focused safe UI check: create one disposable manual visit and confirm it appears in normal history.

Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, persisted model/provenance, validation, tests/device check, commit SHA.
