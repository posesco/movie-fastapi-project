# Workflow Strategy: GitFlow + SemVer

This project strictly follows the **GitFlow** model for branch management and **Semantic Versioning (SemVer)** for version control.

## 1. Main Branches

| Branch | Purpose | Status |
| :--- | :--- | :--- |
| `master` | Production. Only contains stable code ready for the end user. | Always stable. |
| `develop` | Integration. Main branch for daily development. | Latest changes integrated. |

## 2. Supporting Branches

### Feature branches (`feat/*`)
- **Purpose:** Develop new features.
- **Source branch:** `develop`.
- **Destination branch:** `develop`.
- **Convention:** `feat/task-name`.

### Release branches (`release/*`)
- **Purpose:** Prepare a new production release (code cleanup, documentation, versioning).
- **Source branch:** `develop`.
- **Destination branch:** `master` and `develop`.
- **Convention:** `release/vX.Y.Z`.

### Hotfix branches (`hotfix/*`)
- **Purpose:** Fix critical bugs detected in production (`master`).
- **Source branch:** `master`.
- **Destination branch:** `master` and `develop`.
- **Convention:** `hotfix/vX.Y.Z`.

## 3. Semantic Versioning (SemVer 2.0.0)

The version format is **vMAJOR.MINOR.PATCH**:
1.  **MAJOR:** Backward incompatible changes (breaking changes).
2.  **MINOR:** New backward compatible features.
3.  **PATCH:** Backward compatible bug fixes.

### Tags
Each merge to `master` must generate an annotated tag with the corresponding version:
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
```

## 4. Commit Convention (Conventional Commits)

All commit messages must follow the standard:
- `feat:` New feature.
- `fix:` Bug fix.
- `docs:` Documentation changes.
- `style:` Aesthetic changes (formatting, spaces, etc.).
- `refactor:` Code refactoring without functional change.
- `test:` Add or fix tests.
- `chore:` Maintenance tasks (dependencies, configuration).

---
*Note: The Gemini CLI agent must always validate that it is in the correct branch before making any changes.*
