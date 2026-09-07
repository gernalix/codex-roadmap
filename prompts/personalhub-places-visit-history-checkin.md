PROMPT_ID: 726194

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Improve the canonical Places visit/history flow in one coherent task: correct overlapping-place check-in disambiguation, support explicit manual check-in both now and retroactively, and add “Dov'ero?” queries over the resulting unified history.

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

### Manual check-in — now and retroactive
- Add a clear manual check-in action for a selected Place, available without relying on GPS/geofence detection.
- The normal manual action records the selected Place at the current time using the same canonical visit/check-in model as automatic/Timer-backed history, never a parallel table/system.
- Also allow the user to choose a past check-in date/time for a retroactive check-in. Allow an explicit checkout/end date-time when needed to represent a completed historical visit.
- A current manual check-in should create/open the canonical current visit only if the existing model safely supports it. If another open/conflicting visit exists, reuse the canonical transition/conflict semantics or require an explicit user choice; never silently create overlapping open visits.
- A retroactive visit may be open-ended only when that is valid in the canonical model and does not conflict with later history; otherwise require an end time.
- Reject checkout-before-checkin, impossible/conflicting overlaps and accidental duplicates according to current domain rules.
- Repeating “check-in now” for the same already-active Place must be idempotent or report that it is already active rather than creating a duplicate visit.
- Preserve cheap provenance if already supported without forking downstream queries. Manual and retroactive check-ins must appear in the normal history/stats and survive reopen.

### “Dov'ero?”
- Provide date+time selection.
- If the instant falls inside a recorded canonical visit, show that Place.
- Otherwise show immediately preceding and following recorded Places and describe the interval as traveling/going from former to latter. Handle only-previous, only-next and no-data explicitly; never fabricate route/location.
- Query efficiently with targeted/indexed lookups; add an index only if justified by the actual query.

## Tests / acceptance
Cover 0/1/2+ overlap candidates including >10m center-distance difference, cancellation and selected persistence; manual check-in now, duplicate-now behavior and existing-open-visit conflict; valid retroactive interval, boundary/conflict/duplicate validation and reopen; “Dov'ero?” inside visit, exact boundaries, between visits, only previous, only next and no data. Perform one focused safe UI check for current manual check-in, retroactive check-in and a representative “Dov'ero?” result.

No GPS/geofence redesign, route inference, Maps API work, sorting/map redesign or unrelated Places cleanup. Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, overlap policy, manual/retroactive check-in model and validation, Dov'ero query semantics, tests/device check, commit SHA.
