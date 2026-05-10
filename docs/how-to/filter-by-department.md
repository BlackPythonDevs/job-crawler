# Filter jobs by department

Each board can carry an allowlist of department names. Jobs whose department isn't on the list won't be posted.

## Add an allowlist to a board

In `config.toml`:

```toml
[[boards]]
url = "https://boards-api.greenhouse.io/v1/boards/temporaltechnologies/jobs"
departments = ["Engineering", "Developer Relations"]
```

Match is case-insensitive but **exact** — `"engineering"` matches `"Engineering"` but not `"Engineering & Platform"`.

## Find department names

Department names come from the board itself. Easiest way to discover them:

```bash
curl -s 'https://boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true' \
  | jq -r '.jobs[].departments[].name' | sort -u
```

For Rippling, departments live under each job's `department.label`.

## No filter

Omit `departments` (or set it to an empty list) and every job from that board will post:

```toml
[[boards]]
url = "..."
```

## Per-board, not global

Each `[[boards]]` entry has its own list. Two boards with overlapping department names need the list duplicated on each — there is no shared/global allowlist. This is by design: department naming differs across companies.

## See also

- [`config.toml` reference](../reference/config-toml.md)
- [Add a new job board](add-a-board.md)
