# Semantic Versioning Policy

KuroAI strictly adheres to [Semantic Versioning 2.0.0](https://semver.org/).

Format: `MAJOR.MINOR.PATCH[-PRERELEASE]`

---

## 1. MAJOR Version (`X.0.0`)

Incurred when **breaking changes** are introduced to public API signatures or architectural laws.
- Changing `AgentRuntime.run_task()` or `ContextEngine.build_context()` signatures.
- Modifying `backend.contracts` Pydantic model contracts in a non-backward-compatible manner.

---

## 2. MINOR Version (`1.X.0`)

Incurred when **new capabilities or features** are added in a backward-compatible manner.
- Adding a new Agent type or Inference Provider.
- Adding new public engine utility methods without breaking existing signatures.

---

## 3. PATCH Version (`1.0.X`)

Incurred for **backward-compatible bug fixes and performance optimizations**.
- Fixing internal engine bugs or edge-case handling.
- Documentation updates or CI pipeline refinements.

---

## 4. Release Candidates (`1.0.0-rcN`)

Release candidates represent stabilization and hardening phases before a major/minor release.
- `rc1`: Architecture freeze
- `rc2`: Production hardening (telemetry, security, resilience)
- `rc3`: Open-source repository engineering & DX
