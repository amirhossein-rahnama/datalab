# Webhooks

Webhooks let external services react to events happening in your NimbusBoard workspace
in real time, without polling the API. Configure them at Settings > Developer > Webhooks
by giving NimbusBoard a destination URL and selecting which event types to subscribe to -
for example issue.created, issue.status_changed, comment.created, or project.archived.

Each event is delivered as an HTTP POST with a JSON body describing what changed, plus an
X-NimbusBoard-Signature header - an HMAC-SHA256 signature of the raw request body, signed
with the webhook's secret (shown once at creation, like an API key). Verify this
signature before trusting the payload, since anyone who knows your endpoint URL could
otherwise send forged events.

If your endpoint doesn't respond with a 2xx status within 5 seconds, NimbusBoard retries
delivery with exponential backoff: after 1 minute, 5 minutes, 30 minutes, and finally 4
hours, for up to 6 attempts total. After the sixth failed attempt the event is dropped and
logged in the webhook's Delivery history, where you can inspect the exact payload and
response for any past attempt and manually redeliver it. Webhooks share nothing with the
rate limits described in api-rate-limits.md - outbound webhook deliveries don't count
against your API request budget.
