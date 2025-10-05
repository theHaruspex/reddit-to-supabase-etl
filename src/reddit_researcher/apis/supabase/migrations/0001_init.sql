-- Runs table
create table if not exists public.runs (
  run_id text primary key,
  started_at double precision,
  ended_at double precision,
  elapsed_sec double precision,
  subreddit text,
  listing text,
  post_limit integer,
  comment_sample integer,
  replace_more_limit integer,
  qpm_cap integer,
  raw_json integer,
  posts_count integer,
  comments_total integer
);

-- Posts table
create table if not exists public.posts (
  id text primary key,
  subreddit text,
  title text,
  selftext text,
  url text,
  domain text,
  author text,
  created_utc text,
  score integer,
  num_comments integer,
  over_18 boolean,
  upvote_ratio double precision,
  permalink text,
  retrieved_at text
);

-- Comments table
create table if not exists public.comments (
  id text primary key,
  link_id text,
  parent_id text,
  subreddit text,
  author text,
  body text,
  created_utc text,
  score integer,
  depth integer,
  retrieved_at text
);

-- Membership tables
create table if not exists public.runs_posts (
  run_id text not null,
  post_id text not null,
  primary key (run_id, post_id)
);

create table if not exists public.runs_comments (
  run_id text not null,
  comment_id text not null,
  primary key (run_id, comment_id)
);

