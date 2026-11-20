-- Syed Zohaib Shah, Roll Number: PSEB-2026-010729, Date: 2026-11-20
-- Schema and Seed Data for Part C1: Feed Query Index Experiment
-- Tables: users(500), follows(~2 500), posts(200 000)

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS follows;

CREATE TABLE users (
    user_id   INTEGER PRIMARY KEY,
    username  TEXT NOT NULL
);

CREATE TABLE posts (
    post_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id  INTEGER NOT NULL,
    created_at TEXT    NOT NULL
);

CREATE TABLE follows (
    follower_id INTEGER NOT NULL,
    followee_id INTEGER NOT NULL,
    PRIMARY KEY (follower_id, followee_id)
);

-- 500 users
WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM seq WHERE n < 500)
INSERT INTO users (user_id, username)
SELECT n, 'user' || n FROM seq;

-- 200 000 posts spread over 90 days
WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM seq WHERE n < 200000)
INSERT INTO posts (author_id, created_at)
SELECT
    (n % 500) + 1,
    datetime('2026-01-01', '+' || (n % 7776000) || ' seconds')
FROM seq;

-- ~5 follows per user (~2500 total)
WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM seq WHERE n < 2500)
INSERT OR IGNORE INTO follows (follower_id, followee_id)
SELECT (n % 500) + 1, ((n * 37) % 500) + 1
FROM seq
WHERE (n % 500) + 1 <> ((n * 37) % 500) + 1;

-- The feed query (target: user 42, newest 20 posts from followed authors)
SELECT p.post_id, p.author_id, p.created_at
FROM posts p
JOIN follows f ON f.followee_id = p.author_id
WHERE f.follower_id = 42
ORDER BY p.created_at DESC
LIMIT 20;
