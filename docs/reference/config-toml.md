# `config.toml` schema

The board config is a TOML file with a single key, `boards`, which is an array of tables.

## Schema

```toml
[[boards]]
url = "<string, required>"
departments = ["<string>", ...]   # optional
```

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string | yes | Job board API URL. Must be a Greenhouse or Rippling URL the bot recognizes. |
| `departments` | list of strings | no | Allowlist of department names. Match is case-insensitive, exact. Omit or leave empty to allow all departments. |

## Recognized URL hosts

| Host fragment | Provider |
|---|---|
| `greenhouse.io` | Greenhouse |
| `rippling.com`, `ripling.com` | Rippling |

A URL not matching any of these causes the bot to refuse to start with `ValueError: Unsupported job board URL`.

## Example

```toml
[[boards]]
url = "https://boards-api.greenhouse.io/v1/boards/temporaltechnologies/jobs"
departments = ["Engineering", "Developer Relations"]

[[boards]]
url = "https://api.rippling.com/platform/api/ats/v1/board/anaconda/jobs"
```

## Validation

- Missing file → `FileNotFoundError`.
- File present but no `[[boards]]` entries → `ValueError`.
- Entry without `url` → `ValueError`.

## Path

The path is set by the `JOB_CRAWLER_CONFIG` environment variable (default `./config.toml`).
