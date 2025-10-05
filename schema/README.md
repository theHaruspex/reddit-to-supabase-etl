# Database Schema

ERD (Mermaid):


Upserts:
- posts(id), comments(id), runs(run_id)
- runs_posts(run_id, post_id) DO NOTHING
- runs_comments(run_id, comment_id) DO NOTHING

See sql/ for DDL
