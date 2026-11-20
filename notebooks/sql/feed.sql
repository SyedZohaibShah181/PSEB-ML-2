-- Syed Zohaib Shah, Roll Number: PSEB-2026-010729, Date: 2026-11-20
-- Schema and Seed Data for Part C1: Feed Query Index Experiment
-- Tables: users(500), follows(2,500), posts(200,000)

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS follows;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL
);

CREATE TABLE follows (
    follower_id INTEGER NOT NULL,
    followee_id INTEGER NOT NULL,
    PRIMARY KEY (follower_id, followee_id)
);

CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    body TEXT NOT NULL
);

-- Seed 500 users
WITH RECURSIVE cnt(x) AS (
    SELECT 1
    UNION ALL
    SELECT x + 1 FROM cnt WHERE x < 500
)
INSERT INTO users (user_id, username)
SELECT x, 'user_' || x FROM cnt;

-- Seed follower 42 follows 50 users (authors 1 to 50)
WITH RECURSIVE cnt(x) AS (
    SELECT 1
    UNION ALL
    SELECT x + 1 FROM cnt WHERE x < 50
)
INSERT OR IGNORE INTO follows (follower_id, followee_id)
SELECT 42, x FROM cnt;

-- Seed remaining ~2,450 follows across users
WITH RECURSIVE cnt(x) AS (
    SELECT 1
    UNION ALL
    SELECT x + 1 FROM cnt WHERE x < 2500
)
INSERT OR IGNORE INTO follows (follower_id, followee_id)
SELECT (x % 500) + 1, ((x * 7) % 500) + 1 FROM cnt;

-- Seed 200,000 posts across authors with timestamps
WITH RECURSIVE cnt(x) AS (
    SELECT 1
    UNION ALL
    SELECT x + 1 FROM cnt WHERE x < 200000
)
INSERT INTO posts (post_id, author_id, created_at, body)
SELECT 
    x,
    (x % 500) + 1,
    datetime('2026-01-01', '+' || (x * 37 % 30000000) || ' seconds'),
    'Post content message #' || x
FROM cnt;
