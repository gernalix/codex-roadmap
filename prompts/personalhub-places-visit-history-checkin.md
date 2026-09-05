PROMPT_ID: 726194

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Improve the canonical Places visit/history flow in one coherent task: correct overlapping-place check-in disambiguation, add manual historical visits, and add “Dov'ero?” queries over the resulting unified history.

## Exact starting files — verified on PersonalHub/main
Read in grouped passes only:
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInPolicy.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInCapsule.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/HistoryModels.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/visits/VisitMapper.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/visits/VisitUiModel.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/LuoghiHomeViewModel.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/MainActivity.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/home/HomeScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/place/PlaceDetailScreen.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/history/HistoryDialogs.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/ui/history/HistoryScreen.kt`

By this stage history may include Timer-backed intervals; use the canonical visit/query path from prior work. Resolve a renamed/new exact API once if necessary; no directory scan. Increment `version.txt` exactly once by +1.

## Work
### Overlap disambiguation
- zero in-radius candidates: preserve Unknown;
- exactly one: automatic Match;
- two or more: always use explicit Ambiguous selection with all realistic matching candidates; never auto-pick merely because one center is nearer;
- persist only the selected canonical Place ID; cancellation creates no check-in.

### Manual historical visit
- Add a clear Place action to create a manual visit with check-in/check-out date/time; open visit only if safely supported by the canonical model.
- Use the same canonical history model as automatic/Timer-backed visits, not a parallel table/system.
- Reject checkout-before-checkin, conflicts/overlaps and accidental duplicates according to current domain rules.
- Preserve cheap provenance if already supported without forking downstream queries. Manual visits appear in normal history/stats and survive reopen.

### “Dov'ero?”
- Provide date+time selection.
- If the instant falls inside a recorded canonical visit, show that Place.
- Otherwise show immediately preceding and following recorded Places and describe the interval as traveling/going from former to latter. Handle only-previous, only-next and no-data explicitly; never fabricate route/location.
- Query efficiently with targeted/indexed lookups; add an index only if justified by the actual query.

## Tests / acceptance
Cover 0/1/2+ overlap candidates including >10m center-distance difference, cancellation and selected persistence; valid manual historical interval, boundary/conflict/duplicate validation and reopen; “Dov'ero?” inside visit, exact boundaries, between visits, only previous, only next and no data. Perform one focused safe UI check for manual visit and representative “Dov'ero?” result.

No GPS/geofence redesign, route inference, Maps API work, sorting/map redesign or unrelated Places cleanup. Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, overlap policy, manual-visit model/validation, Dov'ero query semantics, tests/device check, commit SHA.
