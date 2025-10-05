# Database Schema

This schema preserves a history of runs while keeping posts/comments idempotent.

## Narrative
- Each probe execution writes a row to `runs` summarizing configuration and counts.
- Content tables `posts` and `comments` store the latest normalized fields per item (upsert on ID).
- Link tables `runs_posts` and `runs_comments` record which items were included in a given run (PK on the pair), enabling historical queries.

## ERD (Mermaid)
See `schema/erd.mmd` for a raw diagram file. A textual ERD is:
- runs 1..* runs_posts
- runs 1..* runs_comments
- posts 1..* runs_posts
- comments 1..* runs_comments

Columns are defined in the DDL.

## Idempotency (ON CONFLICT)
- `runs(run_id)` updates elapsed and counts.
- `posts(id)` updates score, num_comments, retrieved_at.
- `comments(id)` updates score, retrieved_at.
- `runs_posts(run_id, post_id)` DO NOTHING.
- `runs_comments(run_id, comment_id)` DO NOTHING.

## Applying DDL
- See `schema/sql/0001_init.sql` (copied from `apis/supabase/migrations`).
- Apply via Supabase SQL editor or a Postgres client with DDL privileges.

## Sample queries
- Latest top posts in a run:
```sql
select p.id, p.title, p.score
from runs r
join runs_posts rp on rp.run_id = r.run_id
join posts p on p.id = rp.post_id
where r.run_id = '20251005_045125'
order by p.score desc
limit 20;
```

- Comments count per run:
```sql
select r.run_id, count(*) as comments
from runs r
join runs_comments rc on rc.run_id = r.run_id
group by r.run_id
order by r.started_at desc;
```
