# Multi-User Implementation Guide

This document outlines what it would take to add user isolation to Duckling so each user only sees their own document history and data.

---

## 1. Authentication

You need a way to identify who the user is. Options:

| Approach | Complexity | Pros | Cons |
|----------|------------|------|------|
| **Session-based** | Low | Reuse existing `session_id` pattern | No login, user identity is vague |
| **Simple auth middleware** | Medium | Custom users/passwords | You manage passwords and sessions |
| **OAuth/OIDC** | Medium–High | Google, GitHub, etc. | Extra setup, external provider |
| **API keys** | Low | Simple for programmatic use | No interactive UI |
| **Proxy auth** | Low | Delegates to reverse proxy (e.g. nginx) | Depends on infrastructure |

The current `session_id` (Flask session cookie) could be used as a temporary user identifier if you don't need real accounts.

---

## 2. Database changes

### Add `user_id` (or equivalent) to `Conversion`

```python
# models/database.py - Conversion model
user_id = Column(String(255), nullable=False, index=True)  # or session_id for anonymous
```

### Migration

- Add a migration script (like the existing `scripts/migrate_add_document_path.py`) to add `user_id`.
- For existing rows, either:
  - Set `user_id` to a default (e.g. `"anonymous"` or `"legacy"`), or
  - Introduce a `User` table and migrate on first login.

### Index

Add an index on `user_id` for history queries.

---

## 3. Backend: service layer

### `HistoryService`

In `backend/services/history.py`, all queries that read conversions must filter by user:

```python
# Example: get_all
def get_all(self, user_id: str, limit=50, offset=0, status=None):
    with get_db_session() as session:
        query = session.query(Conversion).filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        entries = query.order_by(desc(Conversion.created_at)).offset(offset).limit(limit).all()
        return [entry.to_dict() for entry in entries]
```

The same pattern applies to:

- `get_entry(job_id)` → must also check `user_id` (or treat as 404 if not owned)
- `get_recent`
- `get_stats`
- `search`
- `delete_entry`
- `delete_all` → delete only that user's entries
- `cleanup_old_entries` → only that user's entries
- `reconcile_from_disk` → need a decision for orphaned outputs (e.g. assign to a default user or skip)

### `create_entry`

When creating a conversion, pass `user_id`:

```python
def create_entry(self, job_id, filename, ..., user_id: str):
    entry = Conversion(
        id=job_id,
        user_id=user_id,  # NEW
        filename=filename,
        ...
    )
```

---

## 4. Backend: routes

### Resolve user identity

Create a helper that returns the current user (or session) from the request:

```python
def get_current_user_id() -> str:
    """From session, JWT, OAuth, or proxy header."""
    if current_user.is_authenticated:
        return current_user.id
    return session.get("session_id", str(uuid.uuid4()))  # anonymous fallback
```

### Update calls

Every route that uses history or conversion must pass this user context:

| Route | Change |
|-------|--------|
| `GET /history` | `history_service.get_all(get_current_user_id(), ...)` |
| `GET /history/recent` | same |
| `GET /history/<job_id>` | pass user; return 404 if not owned |
| `DELETE /history/<job_id>` | pass user; 404 if not owned |
| `DELETE /history` | clear only current user's history |
| `GET /history/stats` | stats for current user only |
| `GET /history/search` | search only current user's entries |
| `GET /history/<job_id>/load` | verify ownership before loading |
| `POST /history/reconcile` | assign reconciled entries to current user or a default |
| `POST /convert` | `history_service.create_entry(..., user_id=get_current_user_id())` |
| All convert variants (URL, batch, etc.) | same |

### Convert routes

Ensure all conversion endpoints (`upload_and_convert`, `convert_from_url`, batch, etc.) pass `user_id` into `history_service.create_entry`.

### Status/result routes

`GET /convert/<job_id>/status` and `GET /convert/<job_id>/result` should either:

- Rely on history (which is user-scoped), or
- Validate ownership before returning data.

---

## 5. Output file access

`OUTPUT_FOLDER / job_id` is already per-job. The important part is that:

- `get_entry(job_id)` only returns entries for the current user.
- Any route that serves files (images, tables, exports) must first check ownership via `get_entry` before serving.

Existing validation on `job_id` (path traversal, etc.) stays in place.

---

## 6. Frontend

- If you add login: login screen, logout, and a way to send auth (cookie, Bearer token, etc.).
- If you stay session-based: no login UI; the backend just uses the session cookie.
- API client: ensure cookies or auth headers are sent with all requests (usually automatic for same-origin).

---

## 7. Settings vs history

`UserSettings` is already keyed by `session_id`. For multi-user:

- Option A: Keep `session_id` as the user key, and use the same value for history (`user_id = session_id`).
- Option B: Introduce real users and switch `UserSettings` to `user_id` (or link it to users).

---

## 8. Reconciliation

`reconcile_from_disk()` creates entries for outputs that have no DB row. Deciding who owns them:

- Option A: Assign to a default user (e.g. `"recovered"`).
- Option B: Allow only admins to run reconcile and assign to a chosen user.
- Option C: Skip reconciliation in multi-user mode (or restrict it).

---

## 9. Testing

- Add tests for ownership: user A cannot see/modify user B's history.
- Test `get_entry`, `delete_entry`, `get_all`, `get_stats`, `search`, and all convert and load endpoints.
- Test `reconcile` behavior if you keep it.

---

## 10. Rough effort by approach

| Approach | Backend | Frontend | DB/migration | Total |
|----------|---------|----------|--------------|-------|
| **Session-based** (use existing `session_id`) | 2–3 days | Minimal | 0.5 day | ~3–4 days |
| **Simple auth** (login/password) | 4–5 days | 1–2 days | 0.5 day | ~6–8 days |
| **OAuth** (e.g. Google) | 5–7 days | 2–3 days | 0.5 day | ~8–11 days |

---

## Summary

Core changes:

1. Add `user_id` (or equivalent) to `Conversion` and migrate.
2. Add `get_current_user_id()` and use it in all routes.
3. Filter all history reads/writes by `user_id`.
4. Ensure ownership checks before serving any history or conversion data.
5. Decide how to handle reconcile and orphaned outputs.

The smallest change is to use the existing `session_id` as `user_id`: no login UI, and each browser session is effectively a user.
