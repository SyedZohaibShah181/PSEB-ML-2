# Exploration Homework (Part C)

Short write-ups for C1–C4 in my own words. Sources listed at the end.

## C1 — Optimized Query System of a Social Media Algorithm

### Experiment
- SQLite DB with `users(500)`, `posts(200 000)`, `follows(~2 500)`.
- Query: newest 20 posts from the set of users user 42 follows.
- Tested with and without `CREATE INDEX idx_posts_author_created ON posts(author_id, created_at DESC)`.

### EXPLAIN QUERY PLAN — without index
```text
(5, 0, 216, 'SCAN p')
(7, 0, 45, 'SEARCH f USING COVERING INDEX sqlite_autoindex_follows_1 (follower_id=? AND followee_id=?)')
(25, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

### EXPLAIN QUERY PLAN — with index
```text
(6, 0, 56, 'SEARCH f USING COVERING INDEX sqlite_autoindex_follows_1 (follower_id=?)')
(10, 0, 62, 'SEARCH p USING INDEX idx_posts_author_created (author_id=?)')
(29, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

### Timings
| Setup | Time (ms) | Speedup |
|---|---|---|
| No index | 176.06 ms | 1.0x |
| Composite index on `(author_id, created_at DESC)` | 2.08 ms | 84.8x |

### Why the naive query is slow at scale
Without an index, SQLite must scan the entire `posts` table (200,000 rows here; billions at production scale), join to `follows`, and then sort the result by `created_at DESC` — the `USE TEMP B-TREE FOR ORDER BY` line in the plan is the giveaway. Every step is O(N log N) in the number of posts. At 10⁹ posts, this is seconds per feed refresh.

### What the index changes
The composite index `(author_id, created_at DESC)` stores posts already ordered by author and recency. SQLite uses `SEARCH p USING INDEX` to jump straight to each followed author's slice and walks the index **in descending created_at order** — no separate sort. The `USE TEMP B-TREE` step vanishes, and the query stops after `LIMIT 20` because the first 20 rows in index order are exactly the newest.

### When to precompute feeds instead
A read-time indexed join works at mid-scale. It fails when (a) a user follows high-volume accounts (the join is dominated by those authors), (b) read latency SLO <20 ms is required, or (c) the feed has non-recency ranking (the ranker has to run somewhere). At that point, fan-out on write materialises each post into follower feeds, trading write amplification for instant reads. A hybrid — precompute top-200 candidates per user offline, re-rank online — is what production feeds actually do.

### What this experiment shows
The measured speedup (84.8x) with one index and zero change to application code demonstrates why indexing is the first lever for read-heavy workloads. Precomputation only becomes necessary when fan-out or ranking complexity makes the indexed join itself the bottleneck.

## C2 — GitHub Actions, rules, PR rules and code reviews

<!-- fill after CI workflow -->

## C3 — Theory of System Design

### Glossary (10 terms, one concrete example each)

1. **Load balancer** — Distributes incoming requests across multiple servers so no single one is overwhelmed. *Example:* an AWS ELB sitting in front of three web servers; health checks remove a dead server from rotation.

2. **Horizontal scaling** — Adding more machines rather than making one machine bigger. *Example:* running 10 stateless Node.js processes behind a load balancer instead of one giant server.

3. **Vertical scaling** — Making a single machine more powerful (more CPU/RAM). *Example:* upgrading a database server from 16 GB to 64 GB RAM to fit the working set in memory.

4. **Cache** — A fast-access store of previously computed results. *Example:* storing user profile JSON in Redis for 60 seconds so 90% of requests skip the database.

5. **CDN (Content Delivery Network)** — Geographically distributed servers serving static assets close to the user. *Example:* CloudFront serving images from an edge node in Frankfurt to a user in Germany instead of the origin in Virginia.

6. **Database replication** — Maintaining copies of a database on multiple nodes. *Example:* a primary Postgres writes changes, two read-replicas serve SELECT traffic, reducing load on the primary.

7. **Sharding (partitioning)** — Splitting a dataset across multiple databases by a key. *Example:* user records split across 16 shards by `hash(user_id) % 16`, so each shard holds ~1/16 of users.

8. **Message queue** — A buffer between producers and consumers for asynchronous work. *Example:* Kafka topic `orders.created` — checkout writes a message, the email service consumes it later, decoupling the two.

9. **CAP theorem** — In the presence of a network partition, a distributed system must choose between consistency and availability. *Example:* a banking ledger chooses consistency (reject writes during partition); a social feed chooses availability (serve stale but responsive).

10. **Idempotency key** — A unique client-supplied identifier that makes retries safe. *Example:* Stripe's `Idempotency-Key` header — if a charge is retried, the server returns the original result instead of double-charging.

### Trade-off: consistency vs availability

A relational database with strong consistency (e.g., Postgres with synchronous replication) will refuse writes if a majority of replicas are unreachable — that's a CP choice under CAP. This is correct for a payments ledger where a duplicate or out-of-order transaction is unacceptable. But for a social feed's "like counter," a duplicate write or a 5-second stale read is harmless, and refusing writes during a partition makes the product feel broken. So feeds typically choose an AP design (e.g., Cassandra with tunable consistency): writes go to the nearest replica, later reconciled, and reads may briefly return stale counts. The right choice depends on the cost of being wrong — money and identity favour consistency; engagement data favours availability.

## C4 — A Workflow for System Design

### My workflow (6 steps)

1. **Clarify requirements** — functional (what it does) and non-functional (scale, latency, durability, cost).
2. **Estimate capacity** — number of users, requests/sec, data size, growth over 12–24 months.
3. **Define APIs** — the 3–5 key endpoints / interfaces between components.
4. **Sketch data model** — core entities, relations, and access patterns.
5. **Draw components** — services, storage, queues, caches, external dependencies; label the data flow.
6. **List risks and trade-offs** — what you deliberately chose not to optimise, what would break first, and how you'd measure it.

I record assumptions in a numbered "Assumptions" block at the top so reviewers can challenge them before reading the design.

### Design doc — "URL Shortener (bit.ly-style)"

**Assumptions**
1. 100 M new URLs per month; 10:1 read:write ratio.
2. URLs older than 5 years are read-only; acceptable to cold-store them.
3. Service returns a 6-char code (base62, ~56 billion combinations — enough for years).
4. Single region is acceptable at launch; multi-region by year 2.

**Requirements**
- Functional: create short link, redirect, analytics per link, optional custom alias.
- Non-functional: redirect p99 < 50 ms; write p99 < 200 ms; durability 99.999%; 5-year retention.

**Capacity estimate**
- Writes: 100 M / 30 days ≈ 40 writes/sec average, ~200/sec peak.
- Reads: 400 reads/sec average, ~2,000/sec peak.
- Storage: 100 M × 1 KB per record ≈ 100 GB/month → 1.2 TB/year → ~6 TB over 5 years. Cheap on S3.

**API**
- `POST /shorten {long_url, custom?} → {code, short_url}`
- `GET /{code} → 301 redirect`
- `GET /stats/{code} → {clicks, top_countries, referrers}`
- `DELETE /{code}` (owner only)

**Data model**
- `urls(code PK, long_url, created_at, owner_id, deleted BOOL)`
- `clicks(code FK, ts, country, referrer)` — append-only, batch-written.
- `owners(id PK, email, quota)` — separate small table.

**Components**
- **API service** (stateless, 2 replicas behind a load balancer).
- **Primary DB** (Postgres for `urls` + `owners`; read replicas serve redirects).
- **Click store** (Kafka → S3 + Athena for analytics, so click writes never touch the primary DB).
- **Cache** (Redis, `code → long_url`, 24 h TTL, 90%+ hit rate expected on hot links).
- **CDN** for the redirect edge (301 is cacheable, saving backend hits).

**Risks & trade-offs**
- *Availability over strict consistency on redirect*: a newly created code may 404 for ~1 s at a replica. Accepted; mitigated by reading primary on miss.
- *No custom-alias global uniqueness check at write* — collision retried on insert. Cheaper than a distributed lock for a rare event.
- *Single region at launch*: simpler and cheaper, but adds ~150 ms latency for users outside the region. Documented, accepted for v1.
- *Analytics are eventually consistent* (minutes lag). Acceptable for user-facing stats; not for billing.
- **First thing to break**: write traffic on the primary DB under viral growth — mitigate by sharding `urls` by `hash(code) % N`.

## Sources

- GitHub Actions documentation — https://docs.github.com/en/actions
- GitHub branch protection — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- SQLite query planner — https://www.sqlite.org/optoverview.html
- SQLite EXPLAIN QUERY PLAN — https://www.sqlite.org/eqp.html
- Martin Kleppmann, *Designing Data-Intensive Applications* (O'Reilly, 2017)
- Martin Fowler, "Design Docs at Google" — https://www.industrialempathy.com/posts/design-docs-at-google/
- Stripe idempotency docs — https://stripe.com/docs/api/idempotent_requests
- Cassandra docs — https://cassandra.apache.org/doc/latest/
