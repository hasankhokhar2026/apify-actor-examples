# Support

For an example bug, open an issue in this repository with the example path, Python version, error message, and a minimal input. Remove tokens and private data first. For Actor execution, billing, or pricing questions, use the Actor's Issues tab on Apify; each reference page links to its listing.

`run_actor.py` defaults to basic validation. Add `--execute` only after reviewing the Actor's current pricing. `APIFY_TOKEN` is required for execution. A validation pass does not prove a target website can be collected or that the request will complete.

If polling stops, a remote run can continue until its configured timeout. Open the Console run URL printed by the script to inspect or abort it. The download limit restricts exported records, not the run's workload. `--budget-usd` requests Apify's charge limit; it is not a guarantee covering all platform fees or pricing models.

The sync reads the default published build. Draft README edits require publication on Apify. A missing Actor retains its historical documentation under Previously listed Actors; availability must be checked on Apify.
