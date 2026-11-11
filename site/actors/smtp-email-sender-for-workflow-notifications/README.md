# SMTP Email Sender for Workflow Notifications

Most scraping and automation pipelines end with "now tell someone." This actor is that last step: point it at your own SMTP account — Gmail, Outlook, Yahoo, SendGrid, Mailgun, Amazon SES, or any other mail server — and it sends one email on your behalf. Trigger it standalone, chain it after another actor finishes, or call it from a webhook so a run's results land in an inbox automatically.

## What this actor does

- Sends a single email per run through the SMTP credentials you provide
- Supports plain text, HTML, or both in the same message
- Adds CC, BCC, and Reply-To addresses, with multiple recipients per field
- Attaches files you supply as base64-encoded content
- Sends from the address in `smtpUser`, so the SMTP username should be the mailbox you want the email to come from
- Reports whether CC, BCC, or a Reply-To address were used, alongside the message's own delivery details

## Output per sent email

- `status` — delivery status (`sent`)
- `to` — recipient address(es)
- `cc` — CC address(es); an empty string when none were set
- `bcc` — BCC address(es); an empty string when none were set
- `subject` — email subject line
- `replyTo` — reply-to address; an empty string when not set
- `hasHtml` — whether an HTML body was included
- `hasText` — whether a plain text body was included
- `attachmentCount` — number of attachments supplied in `attachments` (an entry with invalid or empty data is skipped from the message but still counted here)
- `smtpHost` — SMTP server used to send the message
- `smtpPort` — SMTP port used
- `sentFrom` — sender address (your SMTP username)
- `messageId` — the message's Message-ID header; currently an empty string, because the actor doesn't assign one before sending
- `sentAt` — ISO 8601 timestamp of when the message was sent

A record is written only when the SMTP server accepts the message. If validation or sending fails, the run fails with the reason in its status message and the dataset stays empty.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `to` | string | – | Recipient address(es), comma-separated. Required. |
| `cc` | string | – | CC address(es), comma-separated. |
| `bcc` | string | – | BCC address(es), comma-separated. |
| `subject` | string | – | Email subject line. Required. |
| `text` | string | – | Plain text body. At least one of `text` or `html` is required. |
| `html` | string | – | HTML body. At least one of `text` or `html` is required. |
| `replyTo` | string | – | Address replies should go to, if different from the sender. |
| `attachments` | array | – | Files to attach, each as `{ "filename": ..., "data": "<base64>" }`. |
| `smtpHost` | string | – | SMTP server hostname (e.g. `smtp.gmail.com`). Required. |
| `smtpPort` | integer | `587` | SMTP server port: `587` for STARTTLS, `465` for direct SSL, or any other port your server uses. |
| `smtpUser` | string | – | SMTP login username. Required. |
| `smtpPassword` | string | – | SMTP login password or API key. Required; stored encrypted. |
| `useTls` | boolean | `true` | Encrypt the connection: direct SSL on port `465`, STARTTLS on every other port. Turn off only for servers that accept unencrypted connections (e.g. some port `25` relays). |

### Example: plain report email via Gmail

```json
{
  "to": "team@example.com",
  "subject": "Daily scrape complete",
  "text": "The nightly run finished with 1,204 new records.",
  "smtpHost": "smtp.gmail.com",
  "smtpPort": 587,
  "smtpUser": "you@gmail.com",
  "smtpPassword": "your-app-password",
  "useTls": true
}
```

### Example: HTML report with an attachment and CC via Mailgun

```json
{
  "to": "alice@example.com, bob@example.com",
  "cc": "manager@example.com",
  "subject": "Weekly Export",
  "html": "<h1>Weekly Export</h1><p>See the attached CSV.</p>",
  "attachments": [
    { "filename": "export.csv", "data": "bmFtZSxjb3VudA0KZm9vLDEyMw==" }
  ],
  "smtpHost": "smtp.mailgun.org",
  "smtpPort": 587,
  "smtpUser": "reports@mg.example.com",
  "smtpPassword": "your-mailgun-smtp-password"
}
```

### Example: alert with a custom Reply-To via Outlook / Office 365

```json
{
  "to": "oncall@example.com",
  "subject": "Threshold exceeded",
  "html": "<p>Error rate crossed 5% in the last hour.</p>",
  "replyTo": "alerts@example.com",
  "smtpHost": "smtp.office365.com",
  "smtpPort": 587,
  "smtpUser": "monitoring@yourcompany.com",
  "smtpPassword": "your-mailbox-password"
}
```

## Use cases

- **Run completion alerts** — email a summary the moment a scraper or data pipeline finishes
- **Scheduled reports** — attach a CSV or JSON export and send it on a recurring schedule
- **Threshold monitoring** — fire an email when a webhook detects a condition worth flagging
- **Team notifications** — CC or BCC a distribution list whenever a workflow step completes
- **Lightweight transactional mail** — confirmations, digests, or reminders from a no-code pipeline

## FAQ

**Which mail providers work with this actor?**
Any provider that exposes SMTP, including Gmail, Outlook/Office 365, Yahoo Mail, SendGrid, Mailgun, and Amazon SES. You supply the host, port, username, and password for your own account. Because the From address is always your SMTP username, providers whose username is an email address (Gmail, Outlook, Yahoo, Mailgun) work out of the box. SendGrid (username `apikey`) and Amazon SES (an access-key style username) will usually reject the message, since that username isn't a verified sender address.

**Do I need an app password for Gmail?**
Yes, if your Google account has 2-factor authentication enabled (recommended). Generate one under Google Account > Security > App Passwords and use it as `smtpPassword`.

**Can I send to several people at once?**
Yes. Put comma-separated addresses in `to`, `cc`, or `bcc`.

**Why are `cc` or `replyTo` empty in my output record?**
Those fields reflect what you set on input — if you didn't supply a CC or Reply-To address, the record carries an empty string for that field rather than omitting it.

**Is my SMTP password safe?**
`smtpPassword` is marked as a secret input, so Apify encrypts it at rest and masks it in the console and logs.

**How large can an attachment be?**
This depends on your SMTP provider's own limits (Gmail allows up to 25 MB per message). Keep total attachment size well under that to avoid provider-side rejection.

**What if the SMTP server rejects the connection?**
The run fails with the server's own error message (authentication failure, connection refused, timeout, etc.) so you can correct the host, port, or credentials.

**Can I use port 465 instead of 587?**
Yes. Set `smtpPort` to `465` and keep `useTls` enabled; the actor connects over direct SSL for that port instead of STARTTLS.

**Can I choose a different From address or display name?**
No. The message is sent from the `smtpUser` address exactly as entered. Use `replyTo` if replies should go somewhere else.

**Does this actor store or forward my emails anywhere?**
No. Each run only sends the single message you configure through your own SMTP server; nothing is retained beyond the delivery confirmation record.
