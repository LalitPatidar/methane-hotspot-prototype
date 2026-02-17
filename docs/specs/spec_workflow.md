# Spec Workflow for Day-to-Day Development

## Purpose
Ensure each change is requirements-driven, testable, and aligned with MVP goals.

## Workflow

1. **Select requirement(s)**
   - Reference the requirement IDs in `mvp_system_spec.md` (e.g., FR-2, NFR-1).

2. **Write a feature spec first**
   - Create a short doc under `docs/specs/features/` named:
     - `YYYY-MM-DD_<area>_<feature>.md`

3. **Define acceptance criteria and tests before implementation**
   - Include API contract changes, data artifacts, and UI behavior.
   - Name exact test commands to run.

4. **Implement smallest vertical slice**
   - Prefer end-to-end thin slice over broad partial scaffolding.

5. **Validate + document**
   - Run tests/lint.
   - Update relevant docs (`api_contract`, `detection_method`, `data_sources`) as needed.

6. **Close feature with evidence**
   - Record what passed, what was deferred, and why.

## Feature spec template

```md
# Feature Spec: <title>

## Links
- Parent requirement(s): FR-x, NFR-y
- Related issue: #...

## Problem
<What user or system gap this solves>

## Scope
- In: ...
- Out: ...

## Proposed design
- Data model changes:
- API changes:
- Pipeline changes:
- UI changes:

## Acceptance criteria
1. ...
2. ...

## Test plan
- Unit:
- Integration:
- Manual smoke:

## Rollout/ops
- Commands:
- Backfill/migration:
- Observability additions:

## Risks + mitigations
- ...
```

## Implementation checklist template

```md
- [ ] Spec approved
- [ ] Contract changes documented
- [ ] Tests added/updated
- [ ] Commands updated (if needed)
- [ ] Docs updated
- [ ] CI green
```

## Governance rules
- No implementation PR without linked feature spec.
- No merge without tests or explicit "Why no tests" note.
- No pipeline change without reproducible run command.
