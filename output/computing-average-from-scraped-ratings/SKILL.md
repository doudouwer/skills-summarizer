---
name: computing-average-from-scraped-ratings
description: "Computes an average rating from a scraped list of numeric scores and reports the result rounded to a requested precision. Use when asked to 'calculate the average', 'compute the mean', or 'average these ratings/scores' after collecting values from a webpage or dataset."
compatibility: "Requires Python 3.10+ if using the included script; works across all Agent Skills compatible platforms (Claude Code, Cursor, etc.)"
---

# Computing Average From Scraped Ratings

## Goal
Compute the arithmetic mean of a provided list of numeric ratings/scores and return the value rounded to a specified number of decimal places, with basic validation.

## Instructions
1. **Normalize inputs**
   - The agent should obtain a flat list of numeric values (floats or strings convertible to floats).
   - The agent should also obtain:
     - `expected_count` (optional; e.g., 25 for “first page has 25 films”)
     - `decimals` (default: 2)

2. **Validate before computing**
   - The agent should verify the list is non-empty.
   - If `expected_count` is provided, the agent should verify `len(values) == expected_count`.
     - If not, the agent should stop and request the missing values rather than computing a partial average.
   - The agent should check for obvious non-numeric tokens and remove/repair only if the correction is unambiguous; otherwise request clarification.

3. **Compute mean deterministically**
   - The agent should compute:
     - `total = sum(values)`
     - `mean = total / len(values)`
   - The agent should round using standard rounding to `decimals` places.

4. **Report results**
   - The agent should return:
     - the rounded mean
     - optionally the count and sum (useful for auditability)
   - The agent should match the user’s requested formatting (e.g., “to two decimal places”).

## Examples

### Example 1
**Input:**
- values: `[9.7, 9.6, 9.5]`
- decimals: `2`

**Output:**
- average: `9.60`

### Example 2 (with count check)
**Input:**
- values: `25 ratings scraped from a page`
- expected_count: `25`
- decimals: `2`

**Output:**
- average: `9.37`

## Guidelines
- The agent should prefer running a short script for arithmetic to avoid transcription errors.
- The agent should not invent missing values; if fewer than `expected_count` values are present, the agent should request the remainder.
- The agent should keep the computation step separate from the scraping step; this skill assumes values are already collected.

## Scripts
- `scripts/compute_average.py` can be used to compute and validate the mean.
