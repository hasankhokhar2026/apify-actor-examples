# Bulk Email Deliverability & SMTP Verification

Feed this actor a list of email addresses and it checks each one's real deliverability — not just whether it's formatted correctly, but whether its domain can receive mail, whether it's a disposable or role-based address, and, at the deepest setting, whether the mailbox itself actually exists.

## What this actor does

- Validates email syntax and confirms the domain has valid MX (mail-exchange) records.
- Flags disposable/temporary email domains (matched against a bundled disposable-domain list) and role-based addresses such as `admin@`, `info@` or `support@`.
- Identifies addresses on common free consumer providers such as Gmail, Yahoo or Outlook (matched against a built-in list of domains).
- At the deepest verification setting, connects to the mail server to check whether the specific mailbox exists and whether the domain accepts any address at all (catch-all).
- Returns one record per unique address (duplicates are removed case-insensitively) with a verdict and a confidence score. Checks that were skipped at your chosen depth, or that came back inconclusive, are `null` inside `checks` rather than a guessed true/false.

## Output per email

| Field | Description |
|---|---|
| `email` | The normalized email address that was checked (the trimmed input as typed when the syntax check fails). |
| `verdict` | `valid`, `invalid`, `risky`, `disposable`, or `unknown`. |
| `confidence` | Confidence score from 0 to 100 for the verdict. |
| `checks.syntax` | Whether the address is correctly formatted. |
| `checks.mxRecord` | Whether the domain has valid mail-exchange records. |
| `checks.smtp` | `true` if the mail server accepted the mailbox, `false` if it answered "mailbox not found". `null` unless `verificationDepth` is `deep`, and also `null` in deep mode when the server's answer was inconclusive (timeout, temporary rejection, policy block). |
| `checks.disposable` | Whether the domain is a known disposable/temporary provider. `null` at `basic` depth. |
| `checks.roleBased` | Whether the address is a shared role address (e.g. `support@`). `null` at `basic` depth. |
| `checks.freeProvider` | Whether the domain is a free consumer email provider. `null` at `basic` depth. |
| `checks.catchAll` | Whether the domain accepted mail for a made-up test address at that domain. `null` unless `verificationDepth` is `deep`, or when that test was inconclusive. |
| `mxHost` | The domain's highest-priority mail server hostname; `null` when the syntax check failed or no MX record was found. |
| `reason` | Human-readable explanation for a non-valid verdict; `null` when the verdict is `valid`. |
| `verifiedAt` | ISO 8601 UTC timestamp of when the email was checked. |

If an unexpected error interrupts the check of one address, that address still gets a record: `verdict` is `unknown`, `confidence` is `0`, every `checks` value, `mxHost` and `verifiedAt` are `null`, and `reason` starts with `Verification error:`. When the syntax check fails, the remaining `checks` values are `null`; when no MX record is found, the disposable, role, free-provider, SMTP and catch-all checks stay `null`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `emails` | List of strings | – | Email addresses to verify. Required. |
| `verificationDepth` | String (select) | `standard` | `basic` (syntax + MX only), `standard` (adds disposable/role-based/free-provider checks), or `deep` (adds mailbox-level SMTP verification and catch-all detection). |
| `concurrency` | Integer | `10` | Number of emails verified in parallel (1–50). |

### Example: quick syntax and MX check

```json
{
  "emails": ["user@example.com", "test@gmail.com"],
  "verificationDepth": "basic"
}
```

### Example: standard list-cleaning pass

```json
{
  "emails": ["user@example.com", "admin@tempmail.com", "sales@company.org"],
  "verificationDepth": "standard",
  "concurrency": 20
}
```

### Example: maximum-accuracy deep check

```json
{
  "emails": ["prospect@target-company.com"],
  "verificationDepth": "deep",
  "concurrency": 5
}
```

## Use cases

- **List cleaning** — strip disposable and undeliverable addresses from a mailing list before a campaign.
- **Sign-up form validation** — batch-check addresses collected through a form to catch typos and throwaway domains.
- **Sales list hygiene** — verify prospect emails scraped or purchased elsewhere before outreach.
- **Bounce-rate reduction** — screen a list ahead of sending to avoid hitting invalid mailboxes.
- **CRM data quality** — periodically re-check stored contact emails for ones that have gone stale.

## FAQ

**How accurate is the verification?** `standard` depth catches syntax errors, missing MX records, disposable domains and role-based addresses. `deep` mode adds a mailbox-level SMTP check, but many mail servers rate-limit, greylist or refuse such checks. When that happens `checks.smtp` is `null`, and an address on a domain with MX records is still reported as `valid` with partial confidence, so a `valid` verdict on its own doesn't prove the mailbox exists.

**When is an address marked "risky"?** In `deep` mode the actor also asks the domain's mail server about a made-up address. If the server accepts that too, the domain is treated as catch-all: an accepted mailbox there proves little, so the verdict becomes `risky` and the confidence drops.

**What does an "unknown" verdict mean?** It appears when the check of that address hit an unexpected error. The `reason` field carries the error text and the `checks` values are `null`. A blocked or timed-out SMTP check does not produce `unknown`; see the accuracy answer above.

**Why are some `checks` fields `null`?** Each verification depth only runs a subset of checks, and checking stops early once an address fails syntax or has no MX record. Checks that weren't run, or whose answer was inconclusive, come back as `null` rather than a guessed value.

**What counts as a role-based address?** Addresses like `admin@`, `info@`, or `support@` that are typically shared by a team rather than belonging to one person — these tend to have higher bounce and lower engagement rates.

**Can I verify large batches?** Yes. Raise `concurrency` (up to 50) to speed up large lists. Records are written to the dataset once every address has been checked, so the dataset stays empty until the run is nearly finished.

**Does this rely on any third-party verification service?** No. MX and SMTP checks query DNS and the domain's own mail servers directly, and the disposable, role and free-provider checks use lists bundled with the actor.
