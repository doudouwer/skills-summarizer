---
name: retrieving-movie-box-office-revenue
description: "Retrieves a film's box office revenue (and optionally budget) by resolving the correct movie entity and reading the revenue field from movie metadata. Use when asked 'how much did [movie] make at the box office', 'box office gross', 'revenue', or similar performance questions about a specific film title."
compatibility: "Works across all Agent Skills compatible platforms (Claude Code, Cursor, etc.)"
---

# Retrieving Movie Box Office Revenue

## Goal
Return a movie's box office revenue (gross) in a user-ready answer by querying the movie database, resolving the correct title, and extracting the `revenue` field.

## Instructions

### 1) Parse the user request (low freedom)
- Identify the target **movie title** from the question.
- Identify the requested metric:
  - If the user asks about **box office / gross / made**, map to **`revenue`**.
  - If the user asks about **budget**, map to **`budget`**.

### 2) Resolve the movie entity (medium freedom)
1. Call `/movie/get_movie_info` with `query: <movie title>`.
2. If multiple candidates exist, select the best match using:
   - Exact/near-exact title match (case-insensitive)
   - Release year/date if mentioned by the user
   - Original title vs localized title
3. Extract the movie `id` from the chosen candidate.

### 3) Confirm details by ID (low freedom)
- Call `/movie/get_movie_info_by_id` with `query: <movie id>`.
- Treat the by-id response as authoritative for numeric fields.

### 4) Extract and format the answer (medium freedom)
- Read `revenue` from the by-id payload.
- If `revenue` is `0`, `null`, or missing:
  - State that box office revenue is not available in the dataset.
  - Optionally provide release date and other available metadata.
- If `revenue` is present and > 0:
  - Report it as a currency amount (USD if the dataset is USD; otherwise avoid asserting currency).
  - Include the movie title and (if available) release year/date for disambiguation.

### 5) Guardrails / negative routing (low freedom)
- Do **not** use finance/stock endpoints (e.g., `/finance/get_detailed_price_history`) for movie box office questions.
- Do **not** fall back to generic entity search (e.g., `/open/search_entity_by_name`) unless the movie endpoint returns no candidates.

## Examples

### Example 1
**User:** "How much did Neverwas make at the box office?"

**Tool calls:**
1. `/movie/get_movie_info` `{ "query": "Neverwas" }` → choose id `22473`
2. `/movie/get_movie_info_by_id` `{ "query": 22473 }` → `revenue: 11246`

**Assistant answer:**
"*Neverwas* (2005) has a reported box office revenue of 11,246 in the dataset."

### Example 2
**User:** "What was the box office gross for [Movie Title]?"

**Assistant behavior:**
- Resolve the best matching movie via `/movie/get_movie_info`.
- Confirm via `/movie/get_movie_info_by_id`.
- Return the `revenue` value or explicitly say it is unavailable.

## Guidelines
- Prefer `/movie/*` endpoints for film performance metrics.
- Always confirm numeric fields via the by-id endpoint before answering.
- When ambiguity exists, ask a clarifying question (e.g., "Which year/version?") rather than guessing.
- Keep the final response short: title + year + revenue (or unavailability statement).