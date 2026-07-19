# Exporting Your Data

You can export your NimbusBoard workspace data at any time - there's no lock-in, and
exports are available on every plan, including after a workspace has been downgraded or
is in the read-only billing state described in billing.md.

From Settings > Data > Export, choose a format:

- CSV - one file per entity (issues, projects, comments, users), best for spreadsheets
  or quick analysis.
- JSON - a single archive with the full object graph and relationships intact, best for
  migrating into another tool or your own database.
- PDF - a formatted, read-only snapshot of a single project, best for sharing a
  point-in-time report with people who don't have a NimbusBoard account.

Exports are generated asynchronously: request one and NimbusBoard emails you a download
link when it's ready, usually within a few minutes for workspaces under 10,000 issues and
up to an hour for very large workspaces. Download links expire after 7 days for security;
you can request a new export at any time at no charge.

You can also export a single project's issues on demand from that project's "..." menu >
Export project (CSV), without waiting for the full-workspace job - this is the fastest
option when you only need one project's data. The full-workspace export is the only
option that includes cross-project data such as shared labels, workspace-level custom
fields, and the audit log.
