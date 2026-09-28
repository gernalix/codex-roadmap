PROMPT_ID=344032

# PersonalHub AGP built-in Kotlin artifact wiring

Diagnose and minimally fix AGP 9 built-in Kotlin output wiring so the public classes from `:core:hub-context` are present in its outgoing compile/runtime artifacts and consumers such as `:core:alerts` resolve them.

Acceptance criteria:
1. Artifact-level readback proves `WorkflowyIntegrationSettings`, `WorkflowyLinkPolicy`, `WorkflowyHubBridge`, and `SharedTagEngine` are packaged or otherwise on the consumer compile classpath.
2. `./gradlew :core:alerts:compileDebugKotlin --quiet --console=plain` passes.
3. `./gradlew :app:lintDebug --quiet --console=plain` reaches and passes lint.
4. Keep the fix limited to necessary AGP/Kotlin artifact wiring; no broad Gradle upgrade/refactor.

Use an isolated PersonalHub worktree. Do not modify unrelated History or Datasette work, and do not install to a device.
