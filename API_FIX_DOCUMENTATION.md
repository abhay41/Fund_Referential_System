# API Fix: Fund Search Endpoint

## Issue
The `/funds/search` endpoint was not returning any data when called without filters.

## Root Cause
1. **Route Ordering Issue**: In FastAPI, route order matters. The `/{fund_id}` route was defined before the `/search` route, causing FastAPI to interpret "search" as a `fund_id` parameter instead of matching the search endpoint.

2. **Response Format Mismatch**: The response structure needed to be consistent with what the frontend expected.

## Changes Made

### Backend (`backend/app/api/routes/funds.py`)

1. **Reordered Routes** - Moved `/search` to the top (most specific routes first):
   ```
   Order now:
   1. /funds/search           (specific path)
   2. /funds/                 (list all)
   3. /funds/code/{fund_code} (specific with prefix)
   4. /funds/{fund_id}/hierarchy/children (specific with suffix)
   5. /funds/{fund_id}        (generic - must be last)
   ```

2. **Enhanced Search Endpoint**:
   - Added more filter parameters: `fund_code`, `fund_id`, `isin`, `fund_type`, `status`, `mgmt_id`
   - Changed pagination from `skip/limit` to `page/page_size` for better frontend compatibility
   - Used `Optional` and `Query` for proper parameter validation
   - Added partial matching with `CONTAINS` for `fund_code` and `isin`
   - Changed response key from `data` to `funds` for consistency

3. **Updated Imports**:
   ```python
   from fastapi import APIRouter, HTTPException, Depends, Query
   from typing import List, Dict, Any, Optional
   ```

4. **Removed Duplicate Route**: Eliminated the duplicate search route that was at the bottom of the file

### Frontend (`frontend/src/components/FundSearch.js`)

1. **Updated Response Parsing**:
   - Changed from `response.data.data` to `response.data.funds`
   - This matches the new backend response structure

## API Endpoint Details

### `/funds/search` (GET)

**Query Parameters:**
- `fund_code` (optional): Partial match on fund code
- `fund_id` (optional): Exact match on fund ID
- `isin` (optional): Partial match on ISIN
- `fund_type` (optional): Exact match on fund type
- `status` (optional): Exact match on status
- `mgmt_id` (optional): Exact match on management entity ID
- `page` (default: 1): Page number (1-indexed)
- `page_size` (default: 10, max: 100): Items per page

**Response:**
```json
{
  "funds": [
    {
      "fund_id": "F000001",
      "fund_code": "FUND001",
      "fund_name": "Example Fund",
      "fund_type": "UCITS",
      "status": "ACTIVE",
      "management_entity": {
        "mgmt_id": "MG000001",
        ...
      },
      ...
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

## Testing

Test the endpoint with:

1. **No filters** (get all funds):
   ```
   GET http://localhost:8000/funds/search
   ```

2. **With filters**:
   ```
   GET http://localhost:8000/funds/search?fund_type=UCITS&status=ACTIVE
   ```

3. **With pagination**:
   ```
   GET http://localhost:8000/funds/search?page=2&page_size=20
   ```

4. **Partial search**:
   ```
   GET http://localhost:8000/funds/search?fund_code=FUND
   ```

## Benefits

✅ All funds returned when no filters provided
✅ Flexible filtering with multiple criteria
✅ Partial matching for fund_code and ISIN
✅ Consistent pagination (page-based instead of skip-based)
✅ No route conflicts
✅ Better frontend/backend integration
