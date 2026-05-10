# Deduplication strategy

The bot must never post the same job twice. The strategy is intentionally minimal.

## The mechanism

Every posted job has its ID written to Valkey:

```
SET job:<id> 1 EX 7776000
```

On the next cycle, before posting anything, the bot pipelines an `EXISTS job:<id>` for every fetched job and discards any that already exist.

That's the entire dedup logic.

## Why a TTL

`JOB_TTL_SECONDS` defaults to 90 days. After that, the key expires and the job becomes eligible to post again. This is deliberate:

- Boards routinely re-list jobs with the same ID after a hiring freeze, an internal-vs-external distinction, or a department restructure. A long-but-finite TTL means we re-announce these — which is usually the right behavior for an opportunities feed.
- Without a TTL, the dedup set grows forever. With one, the set is bounded by how many jobs are *recent*.

## Why Valkey and not SQLite or a flat file

- Valkey is already in the Compose file for nothing else.
- The access pattern (key existence checks, single-key writes) is the simplest possible Redis-shape workload.
- It survives restarts via AOF (`--appendonly yes` in the Compose command).

A SQLite file would also work. The reason not to switch: Valkey gives us atomic SET-with-EX out of the box and no schema to maintain.

## What is **not** the dedup key

We dedupe on **job ID** as returned by the board. Not URL, not title, not content hash. If a board reuses an ID for a different job (rare but possible), the bot won't notice. If a board changes the URL of an existing job (common), the bot correctly does not re-post it.

## Failure modes

- If posting succeeds but the `mark_job_posted` write fails, the job will post again on the next cycle. This is preferable to the inverse (marked as posted but never delivered).
- If Valkey is unreachable at startup, preflight fails and the bot exits. There is no degraded mode that posts duplicates.
