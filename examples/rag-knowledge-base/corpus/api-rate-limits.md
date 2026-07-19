# API Rate Limits

NimbusBoard's REST API enforces per-workspace rate limits so that one workspace's
traffic can't degrade the service for others. Limits are based on your subscription
plan:

- Starter: 60 requests per minute, burst up to 100
- Team: 300 requests per minute, burst up to 500
- Enterprise: 1,500 requests per minute by default, and higher limits are available on
  request

Every API response includes three headers so you can track your usage without guessing:
X-RateLimit-Limit (the ceiling for your plan), X-RateLimit-Remaining (requests left in
the current window), and X-RateLimit-Reset (Unix timestamp when the window resets). When
you exceed your limit, the API returns HTTP 429 Too Many Requests with a Retry-After
header telling you how many seconds to wait.

Rate limits apply per workspace, not per API key - if you use multiple keys against the
same workspace, they all draw from the same shared budget. Bulk operations (exporting
large datasets, syncing thousands of issues) should use the paginated list endpoints with
a reasonable page size (100-500 items) rather than looping over single-item GET requests,
both to stay comfortably under the limit and because paginated endpoints are
significantly faster per item.
