---
name: use-spark
description: "Interrogation des emails, calendrier et contacts Spark via la CLI locale."
metadata:
  version: 1.3.0
  requires:
    bins:
      - spark
---
# Using spark

`spark` is a CLI for the Spark email client. Use it to query the user's mailbox, calendar, contacts, meetings, and team data.

> [!IMPORTANT]
> **Lecture Seule Stricte (Read-Only)** : Spark CLI est utilisé exclusivement en lecture seule (recherche, consultation de threads, inspection des pièces jointes, contacts et calendrier). L'abonnement Spark d'Henri étant en consultation seule, toute commande de création de brouillon (`spark draft`), de modification ou d'envoi (`spark action`, etc.) est STRICTEMENT INTERDITE et techniquement inactive. Tout courriel à rédiger doit être produit dans le chat Antigravity prêt au copier-coller.

## Running spark

```bash
spark <command> [options]
```

**Environment:** `spark` is a thin client that talks over IPC to the user's running Spark Desktop app - it does not ship its own mailbox, network stack, or credentials. Run it directly on the user's computer against the live Spark Desktop process. Do not try to execute it inside a sandbox, container, CI runner, or any environment isolated from the user's desktop session - it will fail to connect. If Spark Desktop is not running, ask the user to launch it instead of retrying.

## Commands

| Command | Description |
|---------|-------------|
| `accounts` | List accounts, calendars, teams, shared inboxes, and access levels |
| `folders` | List folders/labels with message counts |
| `emails` | List emails with filters and pagination |
| `search` | Hybrid keyword + semantic search with full bodies |
| `thread` | Read full thread - headers, bodies, attachments |
| `attachment` | Read a single email attachment by its ID (auto-downloads) |
| `templates` | List saved message templates (personal and team) |
| `template` | Show a single template by ID or name with its placeholders |
| `comment` | Post a team comment on a thread |
| `events` | List calendar events for a time range |
| `event` | Create, update, delete, or RSVP to a calendar event, including managing attendees / invitations |
| `availability` | Find free time slots, optionally with attendees |
| `contacts` | Search contacts by name or email |
| `team` | Show team info, members, shared inboxes, assignments |
| `meetings` | List meeting transcripts |
| `meeting` | Read a single meeting transcript |
| `action` | Perform actions on emails (archive, pin, snooze, assign, etc.) |
| `contact-action` | Perform actions on contacts (block, accept, categorize, etc.) |

### accounts

List all configured accounts with their calendars, teams, and shared inboxes. Each account and shared inbox shows its **access level** in parentheses, which controls what operations Spark can perform.

```bash
spark accounts
```

Run this first to discover what accounts, calendars, and teams are available, and to check their access levels.

**Access levels:**

| Level | Allowed operations |
|-------|-------------------|
| **read-only** | List, search, and read emails, threads, folders, events, contacts, meetings, teams |
| **triage** | Everything in read-only plus all write operations: drafts, team comments, email actions (archive, move, pin, snooze, assign, etc.), contact actions (block, accept, categorize, etc.) |
| **send** | Everything in triage plus mail-emitting operations: sending drafts (`action send`, including scheduled "Send Later"), and the entire `event` command: `event create` / `event update` / `event delete` / `event rsvp`, including attaching or detaching attendees via `--add` / `--remove` and the iTIP REQUEST / UPDATE / CANCEL / REPLY mail that goes with them. |

Access levels are configured separately for each account and each shared inbox in Spark Desktop under Settings -> AI Agents. Shared inboxes can have a different access level than the parent account - for example, a personal account may have triage access while a shared inbox under the same team is read-only or disabled.

If a command requires a higher access level than the account or shared inbox has, it returns an error with instructions on how to change the level.

### folders

List folders with message counts. Output includes folder identifiers in parentheses - use these as arguments to `emails` and `search`. Mailboxes backed by a Google account show `(Gmail labels)` on the **Email Account** or **Shared Inbox** header. Teams show the team name as a usable identifier for `emails`.

```bash
spark folders                        # all accounts
spark folders user@example.com       # single account
```

### emails

List emails with metadata (ID, From, Date, Subject, Flags). Supports pagination and Gmail-style filters.

```bash
spark emails                                                   # Unified Inbox
spark emails user@example.com:Archive                          # specific folder
spark emails "My Team"                                         # all shared threads in a team
spark emails --filter "from:alice@co.com is:unread"             # filtered
spark emails --filter "newer_than:7d has:attachment"            # recent with attachments
spark emails --page 2 --page-size 20                           # pagination
spark emails --order ascending                                 # oldest first
spark emails --new-senders                                     # show only new sender emails
```

**GateKeeper filtering:** When viewing the Inbox with GateKeeper in explicit mode, new sender emails are automatically filtered out and a "New Senders" count is shown at the top. Use `--new-senders` to view those emails. Use `contact-action acceptContact <email>` or `contact-action blockContact <email>` to accept or block a sender.

**Folder identifier formats** (run `folders` to see available ones):

| Format | Example | Meaning |
|--------|---------|---------|
| Bare name | `Inbox`, `Archive` | Unified folder (cross-account) |
| `email` | `user@example.com` | Account inbox shorthand |
| `email:Folder` | `user@example.com:Archive` | Specific account folder |
| `"Team Name"` | `"My Team"` | All shared threads in a team (quote if spaces) |
| `shared@email:Folder` | `shared@co.com:Inbox` | Shared inbox folder |

**Filter operators** (combinable, Gmail-style):

| Operator | Example |
|----------|---------|
| `from:<addr>` | `from:alice@co.com` |
| `to:<addr>` | `to:bob@co.com` |
| `cc:<addr>` | `cc:team@co.com` |
| `subject:<text>` | `subject:"quarterly report"` |
| `before:yyyy/MM/dd` | `before:2026/03/01` |
| `after:yyyy/MM/dd` | `after:2026/01/01` |
| `newer_than:Xd` | `newer_than:7d` (also `w`, `m`, `y`) |
| `older_than:Xd` | `older_than:30d` |
| `has:attachment` | also `document`, `spreadsheet`, `presentation`, `reminder` |
| `is:unread` | also `read`, `starred`, `pinned`, `unreplied` |
| `is:shared` | emails shared to any team (alias for `is:shared_email`) |
| `is:shared_inbox_open` | open items in shared inbox |
| `is:shared_inbox_done` | completed/closed items in shared inbox |
| `category:personal` | also `priority`, `notification`, `newsletter`, `invitation`, `invitation_response` |
| `assigned_to:me` | emails assigned to current user |
| `assigned_to:<email>` | emails assigned to specific teammate |
| `assigned_to:unassigned` | shared inbox items with no assignee |
| `assigned_to:other` | emails assigned to someone else (not me) |
| `assigned_by:me` | emails delegated by current user |
| `filename:<name>` | `filename:report.pdf` |

### search

Two modes:

- **With a topic (keyword mode):** Hybrid keyword + semantic search returning up to 20 emails with full bodies, sorted by relevance.
- **Without a topic (list mode):** Paged compact table of every email matching `--filter` / `--in` across all folders and all accounts, sorted newest first. Same output as `emails`, but the default scope is "all folders" instead of the Unified Inbox. Trash, Spam, and Blocked are excluded (matching Spark's search field) unless `--in` explicitly targets one of those folders.

```bash
spark search "quarterly report"
spark search "API integration" --filter "from:alice@co.com"
spark search "budget" --in user@example.com:Archive
spark search "vacation" --in user@example.com              # all folders in account

# Keywordless list mode - filter across every folder
spark search --filter "from:alice@co.com"                  # every email from alice, all folders
spark search --filter "from:alice@co.com" --in user@example.com
spark search --filter "is:unread newer_than:7d" --page 2
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<about>` | No | Search topic (positional). Omit to switch to list mode. |
| `--filter` | No | Gmail-style filter (same operators as `emails`) |
| `--in` | No | Scope: account, team, folder, or shared inbox. All folders if omitted. |
| `--page` | No | Page number, 1-based (default: 1). List mode only. |
| `--page-size` | No | Emails per page (default: 50). List mode only. |
| `--order` | No | Sort order: `ascending` or `descending`. List mode only. |

**Use `search` with a topic when the user asks about content** - it returns email bodies so you can answer questions. **Use `search` without a topic when you need to filter emails (especially by `from:`) across every folder** - `emails` only sees the Unified Inbox so it can't answer questions like "every email from alice@co.com, anywhere". Use `emails` for plain browsing of Inbox / one folder.

### thread

Print every message in a thread - headers, full plain-text bodies, and attachment info. After the thread summary line, lists **custom (non-system) folder labels** once for the whole thread, using qualified names like `account@domain.com:MyLabel` (same style as `folders`).

```bash
spark thread 1114                          # by message ID from emails/search output
spark thread --download-attachments 1114   # also fetch attachments via IMAP
spark thread "https://sparkmailapp.com/dpl/bl?token=ABC..."  # by Spark deep link
```

The positional argument accepts either a numeric message ID (the `ID:` line) or a Spark deep link (the `Link:` line) printed by a previous run - `https://sparkmailapp.com/dpl/bl?token=...`, `readdle-spark://bl=...`, or `readdlespark://bl=...`.

Each message's `Attachments:` block is a table with columns `ID`, `Name`, `Size`, `MIME Type`, and `Path`. The `ID` column is the attachment's stable pk - feed it to `attachment` to read the file contents (auto-downloads if necessary). The `Path` column shows the local file or `(not downloaded, ...)` for attachments not yet fetched.

Use `emails` or `search` to find message IDs (the ID column), then `thread` to read the full conversation. Use `folders` to list valid label identifiers for `action attachLabel` / `detachLabel`.

### attachment

Read a single email attachment by its ID (pk) from the `thread` Attachments table. The file is auto-downloaded if it isn't cached locally yet.

```bash
spark attachment 42                          # print metadata (ID, Name, Size, MIME Type, Path, Message ID)
spark attachment 42 --stream > report.pdf    # write raw file bytes to stdout
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<id>` | Yes | Attachment ID (pk) from the `thread` Attachments table. |
| `--stream` | No | Write the raw file bytes to stdout instead of metadata text. Useful inside sandboxed agents that can read the CLI's stdout but not local filesystem paths. The CLI streams the file in 64 KB chunks, so there is no practical size limit. To go the other way - attach a file the app can't read - pipe it into `comment` with `--attach-stream`. |

Use `thread` to find attachment IDs (the `ID` column in the `Attachments:` table). The default text output is one `Key: value` per line, easy to parse from scripts.

### templates

List Spark message templates. Templates round-trip from desktop, so anything saved on the user's computer shows up here.

```bash
spark templates                          # all personal + team templates
spark templates --personal               # only personal templates
spark templates --team "Marketing"       # only that team's templates
spark templates --page 2 --page-size 20  # pagination
```

Output columns: `ID`, `Scope` (Personal / `<team name>`), `Name`, `Subject` (truncated to 40 chars), `Modified`. Use the `ID` or `Name` value with `template <id|name>`.

### template

**Read-only.** Show a single template's full contents and its placeholder requirements.

```bash
spark template 123                       # by ID
spark template "Welcome reply"           # by name (case-insensitive)
```

Output includes scope, recipients, subject, body (HTML stripped to text), attachments, and a `Placeholders:` section listing every placeholder in the template:

- `[auto]` - auto-fillable (recipient/self name). Resolved from `--to` and `--account` when applied.
- `[manual]` - free-form placeholder.

If a name matches more than one template, you'll get an error listing the matching IDs - disambiguate by ID.

### comment

**Requires: triage** access level.

Post a team comment (chat message) on a thread. If the thread is not yet shared, it will be shared automatically. Supports text comments, file attachments, or both. Use `--edit` to update an existing comment.

```bash
spark comment 1234 --body "Looks good, let's proceed."
spark comment 1234 --body "Please review this" --team "Engineering"
spark comment 1234 --body "FYI" --team "Engineering" --user alice@co.com --user bob@co.com
spark comment 1234 --attach /path/to/screenshot.png
spark comment 1234 --body "See attached" --attach /path/to/report.pdf --attach /path/to/data.csv
cat screenshot.png | spark comment 1234 --attach-stream screenshot.png   # pipe a file the app can't read directly
spark comment --edit 5678 --body "Updated comment text"
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<message-id>` | Yes (post) | Message ID of a message in the thread to comment on. |
| `--body` | When no `--attach` | Comment text to post. Required when using `--edit`. |
| `--attach` | When no `--body` | Absolute path to a file to attach. Repeat for multiple files. Each file is sent as a separate message. Cannot be used with `--edit`. The Spark app must be able to read the path; in the sandboxed App Store build a path outside the app's container can't be read and is rejected with a clear error - pipe the file with `--attach-stream` instead. Max 25 MB per file. |
| `--attach-stream` | When no `--body` | Attach a single file whose bytes are read from stdin, shown as `<name>`, sent as its own comment message. Use this when the file is outside the app's sandbox (the App Store build can't read arbitrary paths) - it's the inbound twin of `attachment --stream`. One streamed file per command; cannot be used with `--edit`. Max 25 MB. Example: `cat shot.png \| spark comment 456 --attach-stream shot.png --team "Engineering"`. |
| `--edit` | No | Message ID of an existing comment to edit. Requires `--body`. |
| `--team` | When >1 team | Team name. Required when you belong to multiple teams. |
| `--user` | When team >2 members | Teammate email to share with. Repeat for multiple. Only used when auto-sharing an unshared thread. For teams with 2 or fewer members, the whole team is shared with automatically. |

Use `emails` to find message IDs. Use `thread` to see comment IDs in a conversation. Use `team` to list teams and their members.

### events

List calendar events for a time range.

```bash
spark events                                          # today's remaining events
spark events --tomorrow
spark events --week
spark events --week --in user@example.com             # specific account
spark events --week --in user@example.com:Work        # specific calendar
spark events --start 2026-03-16 --end 2026-03-20      # custom range
```

Date formats: `yyyy-MM-dd`, `dd/MM/yyyy`, or `yyyy-MM-ddTHH:mm`.

Run `accounts` to see available calendar accounts and calendar names.

### event

**Requires: send** access level on the target calendar's owning account. Every mode can emit mail through the calendar service (invitations on create / update, iTIP UPDATE / CANCEL on update / delete of attendee-bearing events, an iTIP REPLY on rsvp), and attaching attendees makes the event discoverable by the provider's invitation channel independent of email, so the whole command sits at `send`.

Create, update, delete, or RSVP to a calendar event, including managing its attendees. Use `--add` / `--remove` on `create` or `update` to attach or detach attendees and send invitations / cancellations through the calendar provider (CalDAV / Google / Exchange).

```bash
spark event create --title "Sync" --start 2026-07-01T12:00 --end 2026-07-01T13:00
spark event create --title "OOO" --start 2026-07-01 --all-day
spark event create --title "Standup" --start 2026-07-01T09:00 --end 2026-07-01T09:15 --video-conference auto
spark event create --title "Sync" --start 2026-07-01T10:00 --end 2026-07-01T10:30 --video-conference zoom
spark event create --title "1:1" --start 2026-07-01T14:00 --end 2026-07-01T14:30 --calendar "user@co.com:Work"
spark event create --title "Sync" --start 2026-07-01T12:00 --add "alice@co.com,bob@co.com"   # create + invite
spark event update ABC-123 --title "New title"
spark event update ABC-123 --location "Room 7"
spark event update ABC-123 --video-conference meet   # add a meeting link
spark event update ABC-123 --add alice@co.com --remove bob@co.com   # swap attendees
spark event delete ABC-123
spark event rsvp ABC-123 accept     # calendar event ID
spark event rsvp ABC-123 decline
spark event rsvp 44268 maybe        # invitation email message ID
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `mode` | Yes | `create`, `update`, `delete`, or `rsvp` (positional). |
| `event_id` | For `update`/`delete`/`rsvp` | Positional, second arg. For `update`/`delete`: a calendar event ID (use `events`). For `rsvp`: either a calendar event ID **or** the message ID of the invitation email (use `emails` / `thread`). |
| `status` | For `rsvp` | RSVP status (positional, third arg): `accept`, `decline`, or `maybe`. |
| `--title` | No | Event title / summary. |
| `--start` | Yes (for `create`) | Start date/time (`yyyy-MM-dd`, `dd/MM/yyyy`, `yyyy-MM-ddTHH:mm`, or `yyyy-MM-ddTHH:mm:ssXXX`). |
| `--end` | No | End date/time. |
| `--all-day` | No | Mark the event as all-day. |
| `--description` | No | Event description / notes. |
| `--alerts` | No | Comma-separated alert offsets (`Ns` for N seconds before, e.g. `300s,600s`) or absolute dates. |
| `--location` | No | Event location text. |
| `--video-conference` | No | Attach a video conference (value required). `auto` auto-picks the account's type (recently used, else default); `meet`, `zoom`, or `teams` selects a specific one and errors if the account doesn't support it. |
| `--calendar` | No | Target calendar for `create`. Format: `email@domain.com` (account's default calendar) or `email@domain.com:Name` (specific named calendar). |
| `--add` | No | Attendee email address(es) to invite (create / update only). Repeat the flag or pass a comma-separated list. New attendees receive an iTIP REQUEST (invitation). |
| `--remove` | No | Attendee email address(es) to remove (update only). Repeat the flag or pass a comma-separated list. Removed attendees receive an iTIP CANCEL. The organizer cannot be removed. |

**Attendees (`--add` / `--remove`):**
- Only valid on `create` and `update`; passing them to `delete` or `rsvp` is refused. Combine both in one `update` to swap attendees - removals run before additions.
- Adding or removing attendees always emits iTIP mail (REQUEST / CANCEL). An event with no attendees stays invisible to the calendar service's invitation channel.
- Attaching attendees makes the event discoverable by the calendar provider's invitation channel (including Google Calendar's same-provider auto-add behavior), independent of email delivery - which is why the whole command requires `send`.

**`event update` semantics:**
- `--video-conference` attaches a meeting link (`meet` / `zoom` / `teams`, or `auto`) to an existing event, generated through the same path as `create`. On an event with attendees this is a shared change, so it sends the iTIP UPDATE.
- Event with **no attendees** → local update, no mail goes out.
- Event **with attendees** → update + iTIP UPDATE sent to all attendees so their calendars reflect the new state. Output reports the attendee count.
- An alerts-only edit is a personal reminder and notifies nobody, even on an event with attendees.

**`event delete` semantics:**
- Event with **no attendees** → local delete, no mail goes out.
- Event **with attendees** → delete + iTIP CANCEL sent to all attendees so their calendars get cleaned up too. Output reports the attendee count. Deleting without the cancellation would orphan the invitation on attendees' calendars (most visibly on Google's same-provider auto-add channel).

**`event rsvp` semantics:**
- Sets *your own* attending status on an invitation: `accept`, `decline`, or `maybe` (alias for tentative). Responding emits an iTIP REPLY back to the organizer.
- The id can be **either** a calendar event ID **or** the message ID of the invitation email. Many providers (Google included) leave an unanswered invite sitting in the inbox without adding it to the calendar, so when the user asks you to respond to an invitation, look it up with `emails` / `thread` and pass that **message ID** - you do not need a calendar event. When the invite *has* been auto-added to the calendar, a calendar event ID works too.
- For a message ID, the reply mirrors Spark Desktop: it updates the matching calendar event if one is synced, otherwise it mails the iTIP REPLY straight to the organizer (and, on `accept`, adds the event to your calendar).
- Errors if the target is not an invitation you can respond to (a plain email, your own organized event with no RSVP, or a provider that does not allow responding).
- For a calendar event, re-RSVPing to the status you already hold is a no-op and reported as such.

Typical flow when scheduling a new meeting: call `event create ...` to lay down the event first, confirm the time and details with the user, then call `event update <event-id> --add ...` to push invitations - so the user can review (or you can revise) the event before any external email goes out. When you already have the attendees, `event create ... --add ...` does both in one step.

Run `accounts` to see writable calendars and the access level on each account.

### availability

Find free time slots. Without `--attendees`, shows the user's own availability. With `--attendees`, computes mutual free windows.

```bash
spark availability                                                        # today
spark availability --tomorrow
spark availability --week --attendees alice@co.com
spark availability --start 2026-03-16 --end 2026-03-20 --attendees a@co.com,b@co.com
```

Free slots are within working hours (08:00-20:00), skip weekends, and ignore events marked "free".

### contacts

Search contacts by name or email. Strict match first, then fuzzy fallback.

```bash
spark contacts "john"
spark contacts "example.com"
```

### team

Show team info - metadata, shared inboxes with members, full member list, assigned emails, assignment summary.

```bash
spark team                     # list available teams
spark team "Readdle"           # specific team
```

### meetings

List meeting transcripts with optional filters and pagination.

```bash
spark meetings
spark meetings --filter "newer_than:30d"
spark meetings --filter "subject:standup" --page-size 10
```

Filter operators: `subject:<text>`, `before:yyyy/MM/dd`, `after:yyyy/MM/dd`, `newer_than:Xd`, `older_than:Xd`.

### meeting

Read a single meeting transcript's summary. Optionally include the full transcript and/or notes.

```bash
spark meeting 42                            # summary only
spark meeting --transcript 42               # include transcript
spark meeting --notes 42                    # include notes
spark meeting --transcript --notes 42       # everything
spark meeting "https://sparkmailapp.com/dpl/bl?token=ABC..."  # by Spark deep link
```

The positional argument accepts either a numeric meeting message ID or a Spark deep link.

Use `meetings` to find meeting IDs.

### action

**Requires: triage** access level.

Perform an action on one or more emails. Supports standard email actions and team actions.

```bash
spark action <action-name> <message-id...> [options]
```

Supported actions:
- `pin` - Pin the message to keep it at the top of the list
- `unpin` - Remove the pin from the message
- `mute` - Mute the thread to stop receiving notifications
- `unmute` - Unmute a previously muted thread
- `snooze` - Snooze the message until a specific date (requires `--date`)
- `unsnooze` - Remove the snooze and return the message to the inbox
- `changeReminder` - Set a follow-up reminder if no reply by the date (requires `--date`)
- `clearReminder` - Remove the follow-up reminder from the message
- `setAside` - Set the message aside for later review
- `archive` - Archive the message, removing it from the inbox
- `moveToInbox` - Move the message back to the inbox
- `moveToTrash` - Move the message to trash
- `moveToFolder` - Move the message to a specific folder (requires `--folder`)
- `attachLabel` - Attach a Gmail or Spark Team label without removing other labels (requires `--folder`)
- `detachLabel` - Remove a Gmail or Spark Team label from the message (requires `--folder`)
- `markAsDone` - Mark the message as done
- `markAsUndone` - Mark the message as not done
- `markAsSeen` - Mark the message as read
- `markAsUnseen` - Mark the message as unread
- `markAsSpam` - Mark the message as spam
- `markThreadAsPriority` - Mark the thread as priority
- `unmarkThreadAsPriority` - Remove the priority mark from the thread
- `unsubscribe` - Unsubscribe from the sender or mailing list
- `changeCategoryPersonal` - Change the email category to Personal
- `changeCategoryNotification` - Change the email category to Notification
- `changeCategoryNewsletters` - Change the email category to Newsletter
- `shareInTeam` - Share the thread with teammates (requires `--team` when multiple teams)
- `assign` - Assign the email to a teammate (requires `--assignee`)
- `delegationComplete` - Mark the delegation as complete
- `delegationReopen` - Reopen a completed delegation

Options:
- `--date` - required for `snooze` and `changeReminder`, optional for `assign` as due date (formats: `yyyy-MM-dd`, `dd/MM/yyyy`, `yyyy-MM-ddTHH:mm`)
- `--folder` - required for `moveToFolder`, `attachLabel`, and `detachLabel` (qualified name: `email@domain.com:FolderName`; use `folders` to list labels including shared inboxes)
- `--team` - team name for team actions; required when you belong to multiple teams
- `--user` - teammate email to share with for `shareInTeam`; repeat for multiple users; required when team has more than 2 members
- `--assignee` - teammate email to assign the email to for `assign`
- `--comment` - comment text for the `assign` action

```bash
spark action pin 12345                                          # pin a message
spark action archive 100 200 300                                # archive multiple messages
spark action markAsSeen 100 200                                 # mark as read
spark action snooze 12345 --date 2026-04-10T09:00               # snooze until date/time
spark action snooze 12345 --date 2026-04-10                     # snooze until date
spark action moveToFolder 12345 --folder "user@example.com:Archive"  # move to folder
spark action attachLabel 12345 --folder "user@gmail.com:MyLabel"       # add Gmail/Team label
spark action detachLabel 12345 --folder "shared@company.com:SomeLabel"  # remove label
spark action changeReminder 12345 --date 2026-04-15             # set reminder
spark action shareInTeam 1234 --team "Engineering" --user alice@co.com  # share with teammate
spark action shareInTeam 1234 --user alice@co.com --user bob@co.com    # share with multiple
spark action assign 1234 --assignee bob@co.com                  # assign to teammate
spark action assign 1234 --assignee bob@co.com --date 2026-04-15 --comment "Please review"
spark action delegationComplete 1234                            # mark delegation done
spark action delegationComplete 100 200 300                     # complete multiple delegations
spark action delegationReopen 1234                              # reopen delegation
```

Use the `emails` command to find message IDs. Use `folders` to resolve qualified names for `moveToFolder`, `attachLabel`, and `detachLabel`. Use `team` to list teams and members for team actions.

### contact-action

**Requires: triage** access level.

Perform an action on one or more contacts by email address.

```bash
spark contact-action <action-name> <email...>
```

Supported actions:

| Action | Description |
|--------|-------------|
| `changeCategoryPersonal` | Change the contact's email category to Personal |
| `changeCategoryNotification` | Change the contact's email category to Notification |
| `changeCategoryNewsletters` | Change the contact's email category to Newsletter |
| `groupEmailsFromContact` | Group emails from the contact by category |
| `groupEmailsFromContactAndShowInInbox` | Group emails from the contact and show in inbox |
| `ungroupEmailsFromContact` | Ungroup emails from the contact |
| `markContactAsImportant` | Enable notifications for the contact |
| `unmarkContactAsImportant` | Disable notifications for the contact |
| `markContactAsPrimary` | Mark the contact as priority (auto-prioritize emails) |
| `unmarkContactAsPrimary` | Remove priority mark from the contact |
| `acceptContact` | Accept or unblock the contact (bypass Gatekeeper) |
| `blockContact` | Block the contact |
| `acceptDomain` | Accept or unblock the contact's entire domain |
| `blockDomain` | Block the contact's entire domain |
| `enableAutosummaryForContact` | Enable auto-summary for emails from the contact |
| `disableAutosummaryForContact` | Disable auto-summary for emails from the contact |

Examples:

```bash
spark contact-action blockContact spammer@example.com
spark contact-action acceptContact alice@co.com bob@co.com
spark contact-action changeCategoryPersonal alice@co.com
spark contact-action markContactAsPrimary ceo@company.com
spark contact-action enableAutosummaryForContact newsletter@example.com
```

Use the `contacts` command to look up email addresses.

## Smart Categories

Spark automatically classifies incoming email into six categories. Use the `category:` filter operator with `emails` and `search` to view mail by category, and use `action` / `contact-action` to reclassify and tune.

| Category | Filter | Typical Content |
|----------|--------|-----------------|
| Priority | `category:priority` | Auto-prioritized or manually marked as priority |
| People | `category:personal` | Direct person-to-person email |
| Notifications | `category:notification` | Service notifications, alerts, receipts |
| Newsletters | `category:newsletter` | Subscriptions, digests, marketing |
| Invites | `category:invitation` | Calendar invitations |
| Invite Responses | `category:invitation_response` | RSVPs, accepts, declines |

**Browse by category** (read-only):

```bash
spark emails Inbox --filter "category:priority is:unread"       # unread priority mail
spark emails Inbox --filter "category:personal is:unread"       # unread people mail
spark emails Inbox --filter "category:invitation"               # pending invites
spark emails Inbox --filter "category:notification is:unread"   # unread notifications
spark emails Inbox --filter "category:newsletter newer_than:7d" # recent newsletters
```

**Reclassify a message** (triage):

```bash
spark action changeCategoryPersonal <id>       # move to People
spark action changeCategoryNotification <id>   # move to Notifications
spark action changeCategoryNewsletters <id>    # move to Newsletters
```

**Tune per-contact category rules** (triage) - changes apply to all future mail from the sender:

```bash
spark contact-action changeCategoryPersonal sender@example.com         # reclassify as People
spark contact-action changeCategoryNewsletters sender@example.com      # reclassify as Newsletters
spark contact-action groupEmailsFromContact sender@example.com         # group by category
spark contact-action markContactAsImportant vip@example.com            # enable notifications
spark contact-action markContactAsPrimary ceo@example.com              # auto-prioritize
spark contact-action enableAutosummaryForContact newsletter@example.com # AI summaries
```

**Category-first triage pattern:** Process inbox in priority order - priority first, then people, then invites, then notifications, then newsletters. This ensures the most important messages get attention first.

## Typical Workflows

**Answer a question about emails:**
1. `spark search "topic"` - find relevant emails with bodies
2. Read the output and answer the user's question

**Find and read a specific email:**
1. `spark emails --filter "from:sender subject:keyword"` - locate the email
2. `spark thread <ID>` - read the full conversation

**Prepare an email reply (Read-only Spark + Chat Draft):**
1. `spark emails --filter "from:sender"` - locate the email
2. `spark thread <ID>` - read the full conversation context
3. Draft the email response directly in the Antigravity chat with Subject and Body, formatted ready for the user to copy-paste into Spark Desktop

**Check someone's schedule for a meeting:**
1. `spark availability --tomorrow --attendees alice@co.com,bob@co.com`
2. Suggest a time from the free slots

**Comment on a shared thread:**
1. `spark emails --filter "from:sender"` - find the email
2. `spark comment <ID> --body "Looks good, approved!"`

**Get team workload overview:**
1. `spark team "Team Name"` - see members and assigned emails

**Look up a contact:**
1. `spark contacts "name or domain"` - find their email address

**Perform an action on emails:**
1. `spark emails --filter "from:sender"` - find the email
2. `spark action archive <ID>` - archive it (or pin, snooze, etc.)

**Share an email with your team:**
1. `spark emails --filter "subject:keyword"` - find the email
2. `spark action shareInTeam <ID> --user alice@co.com` - share with a teammate

**Delegate an email to a teammate:**
1. `spark emails --filter "subject:keyword"` - find the email
2. `spark action assign <ID> --assignee bob@co.com --date 2026-04-15 --comment "Please handle this"`

**Mark delegated emails as done:**
1. `spark emails --filter "subject:keyword"` - find the email(s)
2. `spark action delegationComplete <ID1> <ID2>` - mark multiple as complete

**Find unassigned shared inbox emails:**
1. `spark emails shared@co.com:Inbox --filter "assigned_to:unassigned"` - list unassigned items
2. `spark action assign <ID> --assignee bob@co.com` - assign to a teammate

**Review what's assigned to a teammate:**
1. `spark emails --filter "assigned_to:bob@co.com"` - see their assignments
2. `spark emails --filter "is:shared_inbox_open"` - all open shared inbox items
3. `spark emails --filter "is:shared_inbox_done"` - completed items

**Manage a contact:**
1. `spark contacts "name or domain"` - find the contact email
2. `spark contact-action blockContact spammer@example.com` - block them (or accept, change category, etc.)

## Keeping this skill up to date

The CLI and this skill share a single version (`metadata.version` in the front-matter above). New features in newer Spark Desktop releases ship with an updated embedded skill. Backward compatibility is guaranteed within a major version, so the commands and flags documented here keep working - but newly added features won't appear in this file until it is reinstalled.

Check for an update when - and only when - you hit one of these signals:

- The user asks about a Spark feature, command, or flag that isn't documented here.
- A `spark` command fails with an "unknown command" or "unknown option" error you didn't expect.
- The user explicitly says they upgraded Spark or that the skill is out of date.

In those cases:

```bash
spark --version
```

If the printed version is greater than `metadata.version` above, refresh this file before answering. `spark skill` prints SKILL.md to stdout - capture it and write it back over the file you're reading right now (the path is in your context). For example:

```bash
mkdir -p <parent-of-use-spark>/use-spark
spark skill > <parent-of-use-spark>/use-spark/SKILL.md
```

`<parent-of-use-spark>` is the directory containing the `use-spark/` folder this `SKILL.md` lives in. If you have a file-write tool, you can also pipe `spark skill` output directly through it - the CLI itself does not write any files.

Do not check on every session or before every command - this skill is the source of truth unless one of the signals above tells you otherwise.

## Tips

- Always quote multi-word arguments: `spark search "project update"`
- Combine filter operators in a single `--filter` string: `--filter "from:alice@co.com is:unread newer_than:7d"`
- Use `folders` to discover exact folder identifiers before passing them to `emails` or `search --in`
- Use `accounts` to discover calendar names before passing them to `events --in`
- The `search` command is best for topic-based queries; `emails` is best for browsing/filtering by metadata
- `thread` returns the full conversation - use it when you need the complete email text, not just metadata
- Spark CLI is strictly read-only: draft creation and sending are not supported; format email drafts directly in the chat ready for copy-paste
- Use `comment` to post team chat messages on threads - it auto-shares the thread if needed
- Use `action` to perform email actions like pin, archive, snooze, move to folder, and more
- Use `contact-action` to manage contacts - block, accept, change category, toggle auto-summary, and more