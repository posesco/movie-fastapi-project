# Track: Frontend Integration Readiness

## Description
Adjust the API to improve its consumption from a modern frontend (SPA). This includes changing data formats (Form to JSON), standardizing responses, and improving pagination.

## Goals
- [x] Change `POST /user/register` to accept JSON.
- [x] Implement paginated response wrapper with metadata (total items).
- [x] Return `200 OK` with empty list instead of `404` for collections.
- [x] Simplify `POST /movies/` to handle single movie objects.
- [x] Expose movie categories via a new endpoint.
- [x] Update tests to reflect these changes.

## Technical Details
- **Registration:** Update `UserCreate` schema and endpoint to remove `Form()`.
- **Pagination:** Create a generic `PaginatedResponse[T]` schema.
- **Movies:** Add a repository/service method to fetch unique categories.
