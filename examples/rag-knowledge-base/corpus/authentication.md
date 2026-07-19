# Authentication and API Keys

NimbusBoard supports two ways to authenticate: session-based login for the web app
(email + password, or SSO - see sso.md), and API keys for programmatic access.

To create an API key, go to Settings > Developer > API Keys and click "Generate new
key". Keys are shown only once at creation time, so copy them somewhere safe
immediately; NimbusBoard stores only a hash and cannot show you the key again. Each key
is scoped to a single workspace and inherits the permissions of the user who created it -
a key created by a read-only guest cannot write data, even if the underlying endpoint
would normally allow writes.

API requests authenticate by sending the key as a bearer token in the Authorization
header, for example "Authorization: Bearer nb_live_xxxxxxxxxxxxxxxxxxxx". Keys prefixed
nb_live_ work against production data; keys prefixed nb_test_ work against a sandbox
workspace that resets nightly, useful for integration testing without touching real
project data.

Revoke a key any time from the same API Keys settings page; revocation takes effect
within a few seconds. NimbusBoard recommends rotating API keys at least every 90 days
and never committing them to source control - use environment variables or a secrets
manager instead.
