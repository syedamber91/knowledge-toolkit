export const meta = {
  name: 'verify-sdcourse-luc',
  description: 'Dual-examiner verification loop for the sdcourse x lucsystemdesign dual-lens pack',
  phases: [
    { title: 'Questions' },
    { title: 'AnswerAudit' },
    { title: 'Score' },
    { title: 'SignOff' },
  ],
}

// Chapter content mirror — MUST be kept in sync with scripts/generate_sdcourse_luc.py
// CH{n} strings. Phase tasks append entries here; never let this drift from the PDF.
const CHAPTERS = [
  {
    id: 1,
    title: 'Quality Attributes, Trade-offs & the Production Reality Gap',
    content: `Sources: lucsystemdesign — System Design Quality Attributes · sdcourse — Course Structure and Curriculum Design

Summary: Luc supplies the vocabulary for what "good" even means in a system — attributes, pillars, tactics — and the discipline to admit you cannot maximize all of it at once. sdcourse supplies the reason that vocabulary alone will not save you: there is a gap between knowing the trade-offs and having actually built something that survives them.

Luc's Lens: Attributes Are Goals, Not Features
Most system design failures are not caused by a missing feature. They are caused by a system that cannot hold up once real traffic, real failure rates, and real attackers show up. Luc's framing starts there: slow requests, flaky uptime, tangled code, and weak security are the actual killers, and none of them show up on a feature checklist. Quality attributes — availability, consistency, latency, scalability, reliability, security — are the properties that determine whether a system survives contact with production, and Luc insists they be treated as first-class requirements gathered and negotiated up front, not bolted on after the "real" features are built.

The second half of the lens is a discipline about honesty: you cannot maximize everything simultaneously. Availability competes with cost. Strong consistency competes with global latency. Flexibility competes with simplicity. Every one of these is a dial, and turning one dial up turns another down — there is no configuration where all dials sit at maximum. Luc separates the vocabulary into three layers so the trade-off is easier to reason about: attributes are the goals ("this system should be highly available"), pillars are the strategies that get you there (modularity, redundancy, fault tolerance), and tactics are the concrete mechanisms that implement a pillar (caching, sharding, circuit breakers). Skipping straight to tactics without naming the attribute and pillar behind them is how teams end up with a cache that solves the wrong problem.

Vague targets compound the problem. Saying a system should be "highly available" or "scalable" gives an engineer nothing to design against — it is not falsifiable and it does not survive a design review. Luc's fix is the attribute scenario: a specific what-if statement ("if the payments region goes down, checkout must fail over within 30 seconds with no data loss") that turns an adjective into a testable requirement. Scalability itself gets the same specificity treatment — a scalable system handles more traffic by adding resources, not by rewriting code, and statelessness is what makes that horizontal add-more-boxes move possible in the first place. Reliability, likewise, is reframed away from "it doesn't crash" toward something sharper: predictable behavior under unpredictable conditions. And security is reframed away from a checklist item toward an embedded assumption — secure systems are designed expecting breaches, and the design's job is to constrain the blast radius, not pretend the breach won't happen.

Decision Rule (Luc): Before choosing a tactic, name the attribute it serves and the pillar it implements — and name what you are giving up. If you cannot state the competing attribute you are trading away (cost, latency, simplicity), you have not made a design decision, you have made a guess. When NOT to use a tactic: when you cannot yet write the attribute scenario it is supposed to satisfy — reaching for caching, sharding, or circuit breakers before the requirement is falsifiable just adds complexity in search of a problem.

Luc: "Many systems fail not because a feature is missing, but because the system buckles under real-world pressure: slow requests, flaky uptime, tangled code, or weak security."

sdcourse's Lens: The Gap Between the Map and the Shovel
sdcourse's angle is not about naming attributes — it is about what it actually costs to build a system that satisfies them. The curriculum this examiner grounds itself in is a 254-lesson roadmap spanning Days 1–270, building one continuous artifact: a complete distributed log processing system called LogStream, with a Java/Spring Boot track running in parallel with a Python/JavaScript track over the same material. The course is 80% coding, and the hardware bar is explicit — 16GB RAM required, 8GB minimum "but you'll suffer." None of that detail is decoration; it is sdcourse's way of insisting that quality attributes are not learned by reading about them, they are learned by hitting the failure mode they describe.

That insistence is aimed squarely at a specific failure sdcourse has watched repeatedly: engineers who can recite "CAP theorem," "availability vs. consistency," or "circuit breaker" fluently in an interview but have never built the thing that makes those trade-offs real. Knowing the vocabulary from Luc's lens is necessary but not sufficient — sdcourse's whole curriculum design exists to close the gap between the two. The predictors of who actually closes that gap are concrete and unglamorous: run the code instead of just reading it, treat the GitHub reference repo as a checkpoint rather than a shortcut to copy from, and show up in Discord — of the three, Discord activity is the single best predictor of who finishes.

Table — Signal / Finisher behavior / Lurker behavior:
- Code execution: Finisher runs every day's code, hits real errors, debugs them; Lurker reads the lesson, never executes it.
- Reference repo: Finisher uses it as a checkpoint to compare against; Lurker copies from it as a shortcut.
- Discord activity: Finisher is active — best single predictor of completion; Lurker is absent.
- Hardware: Finisher uses 16GB RAM (course-recommended); Lurker uses 8GB minimum — "but you'll suffer."
- Timeline: Finisher treats 270 days as a reference, not a race; Lurker falls behind and drops rather than resuming.

Production Reality: A student who can define "availability vs. consistency" from a flashcard has not yet paid the cost that makes the definition mean anything. The course is structured around 254 lessons of hands-on output specifically because the failure mode it is designed against is passive consumption — someone who nods along to Luc's attribute/pillar/tactic framework but has never had a tactic fail on them at 2am. sdcourse's answer to "how do I actually learn quality attributes" is not more reading; it is building LogStream day by day and falling behind on purpose, because falling behind and resuming is what the 270-day timeline is built to tolerate.

sdcourse: "There is a massive gap between 'knowing' system design for an interview and 'building' a system that survives a production workload. Most courses give you the map, but they don't give you the shovel."

Diagram callout: Luc hands you the map of trade-offs; sdcourse hands you the shovel to find out what the map didn't show. (LUC box: Name the Trade-off — Attribute → Pillar → Tactic; you can't max everything — write the attribute scenario before picking the tactic. SDCOURSE box: Build the Thing — 254 lessons, 270 days, one system: LogStream; Map ≠ Shovel — run the code, hit the errors.)

Where They Converge / Diverge:
Converge: Both reject vague competence — Luc rejects vague attribute targets like "highly available" in favor of falsifiable scenarios, and sdcourse rejects passive reading in favor of falsifiable execution (run it, hit the error, debug it); each is demanding proof instead of a claim.
Diverge: Luc's unit of rigor is a sentence — an attribute scenario you can write down before you build anything — while sdcourse's unit of rigor is elapsed time and executed code across 270 days; one is a pre-design discipline, the other is a post-design endurance test, and a team can ace the first while still failing the second.

Active Recall questions posed in the chapter:
Q1. A teammate proposes adding a Redis cache to "improve performance." Using Luc's attribute → pillar → tactic decision rule, what two questions must be answered before this tactic is approved?
Q2. According to sdcourse's curriculum data, what is the single best predictor of whether a student finishes the 254-lesson LogStream course, and why does that beat "reads every lesson"?
Q3. Explain the difference between the kind of rigor Luc's attribute scenarios enforce and the kind of rigor sdcourse's 270-day build enforces — why could a team pass one and still fail the other?`,
  },
  {
    id: 2,
    title: 'Consistency Models: CAP, ACID vs BASE, Strong vs Eventual & Multi-Region',
    content: `Sources: lucsystemdesign — CAP Theorem, ACID vs BASE, Strong vs Eventual Consistency · sdcourse — Multi-Region Replication and Distributed Consistency

Summary: Luc supplies the decision framework for consistency — CAP is not a permanent trade-off but a question of what happens when the network splits, and ACID/BASE and strong/eventual are the same question asked at the data-model and read-path layers. sdcourse supplies the number that makes the framework operational: what lag is acceptable, measured in seconds, across real regions.

Luc's Lens: One Question, Asked Three Times
Luc's core reframe of the CAP theorem is that "pick two of three" is catchy but misleading. CAP is not about permanently giving something up — during normal operation, when nodes can talk to each other reliably, a system can have both consistency and availability at once. The trade-off only appears the moment the network actually breaks. CP systems respond to that moment by refusing or delaying operations rather than risk returning something wrong; AP systems respond by continuing to serve, accepting that some responses may be stale. Luc's decision rule collapses this into one question: what hurts your product more — returning incorrect data, or returning no data at all? If incorrect data hurts more, choose CP. If no data hurts more, choose AP. Most real systems don't answer this once for the whole system — they carry a small CP core for writes that must be correct, wrapped in AP layers that serve and cache data quickly across regions.

ACID vs BASE is the same fork restated at the data-model layer. ACID and BASE sit on opposite ends of a spectrum shaped by CAP: ACID favors consistency and correctness even if it means refusing or delaying requests during failures, while BASE favors availability and scale even if it means serving temporarily inconsistent data. The catch Luc flags is that BASE's weakness shows up exactly where it hurts most — "this must never happen" rules, like double-spend, are hard to enforce in real time under an eventually-consistent model. The resolution is the same pattern as CAP: keep a small ACID core for operations that must always be correct, and use BASE layers to serve that data quickly across regions. ACID and BASE aren't rivals to be argued about in the abstract; they're tools suited to different failure modes and different expectations of the reader.

Strong vs eventual consistency is the same fork again, now asked at the read path. Strong consistency guarantees every read reflects the most recent successful write, no matter which replica answers — enforced through quorum confirmation and consensus algorithms like Paxos or Raft. Eventual consistency drops that guarantee: all replicas will converge to the same state over time, using conflict resolution strategies like last-write-wins or version vectors, but a read in the meantime may return outdated data. Luc's guidance is the same CP/AP question in different clothes: use strong consistency when accuracy is non-negotiable — financial transactions, stock levels, systems that coordinate scarce resources — and use eventual consistency when responsiveness and uptime matter most — user feeds, caching, globally distributed services. A banking system can't risk showing a stale balance, so it stops serving until replicas agree; a social app can't freeze every time replicas lose connection, so it shows "good enough" data and syncs later. Notice one important distinction Luc draws explicitly: CAP consistency (every read returns the most recent write across nodes) and ACID consistency (a transaction leaves the database in a valid state per defined rules) are different guarantees that happen to share a word — conflating them is a common source of muddled design conversations.

Decision Rule (Luc): Whichever layer you're deciding at — CAP, ACID/BASE, or strong/eventual — ask the same question: what hurts your product more, returning wrong data or returning no data? If wrong data hurts more, choose the consistent side (CP, ACID, strong). If no data hurts more, choose the available side (AP, BASE, eventual). When NOT to force a single global answer: most real systems need both — a small strongly-consistent core for the operations that must never be wrong, wrapped in an eventually-consistent, highly-available layer for everything else. Treating consistency as one system-wide setting instead of a per-operation decision is the mistake.

Luc: "The common summary is 'pick two of three.' It's catchy, but misleading. CAP is not about permanently giving something up. It's about what happens when the network splits."

sdcourse's Lens: Consistency Is a Number You Measure, Not a State You Achieve
sdcourse's angle on consistency starts from a premise that sounds fatalistic but is meant to be operational: network partitions are inevitable, replication lag is normal, and chasing zero lag is a waste of engineering effort because zero lag is impossible. The right move is not to eliminate lag but to design for partition tolerance with eventual consistency, then measure and optimize for an acceptable lag level — a number with an owner and an alert threshold, not an aspiration. That framing turns Luc's CP/AP decision rule into a concrete operational target: once you've decided a subsystem is AP, the next question sdcourse forces is "how stale is too stale, in seconds?"

For a log processing system specifically, sdcourse argues active-active multi-region is almost always the right call, for a reason grounded in the shape of the workload: logs are append-only, high-volume, and latency-sensitive, so the deduplication cost of merging two regions after a split is far less than the cost of dropping events during an outage. The stakes of getting this wrong are concrete — a single-region log system is an availability bet, and delayed logs are nearly as dangerous as missing logs because they break the correlation windows used for incident diagnosis. Ordering compounds the difficulty: physical timestamps fail across regions because of clock skew, which is why sdcourse reaches for vector clocks to track logical event ordering instead of trusting wall-clock time. On the operational side, Kafka's MirrorMaker 2 is the concrete mechanism sdcourse points to for cross-region replication, using topic-offset translation specifically to prevent replication loops between regions.

Table — Metric / Value / Why it matters:
- MirrorMaker 2 added latency: 50–200ms. Depends on network distance between regions; a floor, not a target.
- Replication lag alert threshold: >10 seconds behind. Region B's consumer offset falling >10s behind Region A's producer offset means you're approaching your RPO budget.
- Ordering guarantee: None from physical clocks. Clock skew across regions defeats timestamp ordering — use vector clocks instead.
- Loop prevention: Topic-offset translation. MirrorMaker 2's mechanism to stop replicated events from replicating back and forth forever.

Production Reality: Replication lag is the single most important operational metric in a multi-region log pipeline — not uptime, not throughput. The concrete threshold sdcourse gives is that if Region B's consumer offset falls more than 10 seconds behind Region A's producer offset, you are approaching your RPO budget, which means the "acceptable lag" from the decision to go eventually-consistent has stopped being acceptable and has become an incident. This is what separates a team that has merely chosen AP from a team that has operationalized it: the AP choice is a design decision made once, but the lag threshold is a number watched every minute.

sdcourse: "Replication lag is the single most important operational metric: if Region B's consumer offset falls more than 10 seconds behind Region A's producer offset, you are approaching your RPO budget."

Diagram callout: Luc tells you which side of the trade-off to stand on; sdcourse tells you the second count at which standing there stops being fine. (LUC box: One Question, 3 Layers — CAP / ACID·BASE / strong·eventual — wrong data or no data? Small consistent core, available layer around it. SDCOURSE box: Put a Number On It — Zero lag is impossible — alert past 10s behind; Vector clocks, not timestamps; active-active for logs.)

Where They Converge / Diverge:
Converge: Both reject the idea that consistency is ever fully "solved" — Luc insists you cannot avoid partitions by trusting your infrastructure, only reduce their frequency, and sdcourse insists network partitions are inevitable and zero replication lag is impossible; both treat the failure mode as permanent background weather to design for, not a bug to eliminate.
Diverge: Luc's unit of decision is qualitative and made once per operation — CP or AP, ACID or BASE, strong or eventual, chosen by asking which failure hurts more — while sdcourse's unit of decision is quantitative and continuously monitored — a 10-second replication-lag threshold and a 50–200ms MirrorMaker 2 floor; a team can correctly choose "AP, eventual consistency, active-active" using Luc's framework and still get paged at 3am because nobody wired the alert sdcourse says the choice requires.

Active Recall questions posed in the chapter:
Q1. Using Luc's decision rule, a checkout service's inventory count and a social app's "likes" counter need different consistency models. Which question does Luc say you should ask for each, and what answer points to CP/ACID/strong vs AP/BASE/eventual?
Q2. Per sdcourse, why does a single-region log system count as "an availability bet," and what specific operational metric and threshold tells you your multi-region replication has crossed from acceptable lag into an RPO problem?
Q3. Luc and sdcourse both treat network partitions as inevitable rather than avoidable. Explain how their responses to that shared premise diverge — one gives a decision you make once, the other gives a number you watch continuously — and why a team could pass Luc's test but still fail sdcourse's.`,
  },
  {
    id: 3,
    title: 'Database Selection & Distributed Query Patterns',
    content: `Sources: lucsystemdesign — Database Selection, SQL vs NoSQL · sdcourse — Distributed Query Engine and Caching Patterns

Summary: Luc supplies the decision framework for picking a store in the first place — stop asking "which database is best" and start asking "what is the hardest question my system asks, every day, under load." sdcourse supplies the production reality of answering that hardest question fast, at scale, on historical data, without the storage bill or the cache exploding.

Luc's Lens: It's a Question Problem, Not a Schema Problem
Luc's central reframe is that choosing a database feels like a schema problem — rows and columns versus documents versus key-value pairs — but it usually isn't. It's a question problem. The core decision rule: pick the database that is built for the hardest question you ask most often. No single database answers every hard question well, and that's not a flaw to engineer around — it's the reason the ecosystem has this many categories. Relational databases give ACID guarantees plus rich SQL joins but scale up more naturally than they scale out. Distributed SQL keeps the same SQL-plus-ACID promise while spreading data across nodes, and you pay for that with network latency and operational complexity. Document databases store each record as a self-contained JSON-like document with no fixed schema, using embedding to cut down on joins. A key-value store is, in Luc's words, basically a distributed dictionary — no schemas, no joins, no complex queries, just fast lookups by key. In-memory databases trade RAM cost and volatility risk for extremely low latency; wide-column stores demand careful up-front modeling because you don't get relational joins for free; time-series databases lean on append-only writes, time partitioning, compression, and downsampling; search engines are usually eventually consistent and were never meant to be your transactional source of truth; and vector databases use approximate nearest-neighbor indexes, which means the speed comes from approximation — you trade perfect accuracy for low latency by design, not by accident.

This is why Luc sees most production systems settle on a primary-plus-secondary pattern rather than a single winner: a primary database chosen for correctness, and secondary databases chosen for access pattern — SQL for transactions, Search for retrieval, Cache for speed, Vector for semantic discovery. The SQL-vs-NoSQL debate is the same question restated at a coarser grain. SQL databases enforce a defined schema and consistent relationships; NoSQL databases relax those rules to handle data that is rapidly changing, wildly varied, or simply massive. SQL scales vertically first and favors strong ACID guarantees; NoSQL scales horizontally through partitioning and replication and often trades strict consistency for availability and speed, favoring the BASE approach — Basically Available, Soft State, Eventually Consistent. Luc's guidance is intentionally plain: choose SQL when data is structured, you need strong consistency, and queries are complex; choose NoSQL when data is flexible, you need horizontal scale, and the application evolves fast. And crucially, many systems use both — SQL for transactions and analytics, NoSQL for caching, sessions, or event data — because the primary-plus-secondary pattern and the SQL-vs-NoSQL choice are really the same underlying move at two different zoom levels.

Decision Rule (Luc): Before picking a store, write down the single hardest question your system asks most often under load — not the easiest one, not the one in the demo. Pick the database built for that question, then add secondary stores for the other access patterns instead of forcing one database to be good at everything. When NOT to use this rule as an excuse: "just use the database we always use" is how many systems paint themselves into a corner — reaching for a familiar default without asking the question is a decision, just an unexamined one. Pick intentionally, design for your future scale, and let your data — not trends, not habit — drive the choice.

Luc: "Choosing a database feels like a schema problem. It usually isn't. It's a question problem."

sdcourse's Lens: Answering the Hardest Question Fast, at Scale, on a Budget
sdcourse's angle picks up exactly where Luc's decision rule leaves off: once you know the hardest question your system asks — for a log processing platform, that's usually "give me a sub-second answer over historical data without me paying to keep all of it hot" — the architecture has to separate how you write from how you read. CQRS is the mechanism: the write side is a high-throughput Kafka ingestion path, and the read side is an optimized query structure with pre-computed aggregations, so reads and writes scale independently instead of contending for the same resources. The cost of that separation is eventual consistency — query results might be 100–500ms behind real-time events — and the payoff is the ability to handle roughly 10x more concurrent queries than a system that reads and writes against the same live table. sdcourse is explicit that this trade only makes sense once you've named the hard question, echoing Luc's framing from the other direction: the architecture follows the query, not the other way around.

Caching is where sdcourse gets most concrete, and most willing to name an anti-pattern outright: never implement write-through caching for high-velocity log data, because the cache invalidation overhead negates the performance benefit and creates consistency nightmares during failure scenarios. Instead, sdcourse lays out a three-tier Redis caching scheme tuned to how log queries actually behave — a query result cache with a 5-minute TTL, an aggregation cache with a 1-hour TTL, and a hot data cache for the last 15 minutes with a 30-second TTL. Because log queries exhibit strong temporal locality — most queries hit recent data — cache hit ratios above 95% are achievable with this tiering. On the storage side, sdcourse names the point at which the naive approach collapses: traditional log tables become unusable beyond 10 million records without a proper indexing strategy, which is the concrete, numeric version of Luc's abstract warning that no single database answers every hard question well.

Table — Layer / Value / Why it matters:
- CQRS query capacity gain: ~10x concurrent queries. Read/write separation lets each side scale independently.
- CQRS staleness window: 100–500ms. The eventual-consistency cost of decoupling reads from writes.
- Query result cache TTL: 5 minutes. Top tier of the three-tier Redis scheme.
- Aggregation cache TTL: 1 hour. Pre-computed rollups change slowly, so they can live longer.
- Hot data cache TTL: 30 seconds, last 15 min. Shortest TTL, covers the highest-churn recent window.
- Achievable cache hit ratio: >95%. Driven by temporal locality — most log queries hit recent data.
- Naive log table failure point: >10M records. Traditional tables become unusable without proper indexing beyond this.

Production Reality: The anti-pattern sdcourse warns against isn't a style preference — it's a failure mode with a specific shape. Write-through caching on high-velocity log data means every write pays a cache-invalidation cost on the hot path, and when that invalidation logic hits a partial failure — a network blip between the write path and the cache layer — you're left with a cache that disagrees with the source of truth and no clean way to reconcile it under load. The three-tier TTL scheme sidesteps this entirely by never trying to keep the cache perfectly in sync with writes; it accepts staleness in fixed, bounded windows (30s / 5min / 1hr) instead, which is a deliberate design choice, not an oversight.

sdcourse: "Anti-Pattern Warning: Never implement write-through caching for high-velocity log data. The cache invalidation overhead will negate performance benefits and create consistency nightmares during failure scenarios."

Diagram callout: Luc tells you which store answers your hardest question; sdcourse shows what it takes to keep answering it in under a second once the data no longer fits in one machine's memory. (LUC box: Name the Hardest Question — Not "which DB is best" — "what question, under load, every day?" Primary for correctness, secondaries for access. SDCOURSE box: Answer It in <1s — CQRS splits read/write — 10x query capacity, 100-500ms lag; 3-tier cache, never write-through — 95%+ hit ratio.)

Where They Converge / Diverge:
Converge: Both reject a single default as an answer — Luc insists "just use the database we always use" is how systems paint themselves into a corner, and sdcourse insists the naive single-table, write-through-cache approach becomes unusable past a specific, named scale (10M records, or any high-velocity write path); both push the reader toward an intentional, workload-driven choice over a habitual one.
Diverge: Luc's unit of analysis is the store itself — pick the right category of database for the hardest question, primary plus secondaries, SQL vs NoSQL by data shape and consistency need — while sdcourse's unit of analysis is the query path around whichever store you picked — CQRS to decouple read and write scaling, a tiered cache with named TTLs to keep 95%+ of queries out of the database entirely. A team can correctly apply Luc's framework and choose the right database category, and still get paged because nobody built the CQRS split or the tiered cache that keeps that correct database answering in under a second at 10x the load.

Active Recall questions posed in the chapter:
Q1. Per Luc's decision rule, what single question should you ask before picking a database, and why does "just use the database we always use" count as a decision rather than a neutral default?
Q2. Per sdcourse, why is write-through caching an anti-pattern specifically for high-velocity log data, and what three TTL tiers does the alternative Redis scheme use instead?
Q3. Luc frames database selection as picking the store built for your hardest recurring question; sdcourse frames it as keeping that store fast once real query volume arrives. Using CQRS and the 10M-record indexing cliff as evidence, explain how a team could pass Luc's test but still fail sdcourse's.`,
  },
  {
    id: 4,
    title: 'Indexing, CDC & Structured Log Data',
    content: `Sources: lucsystemdesign — Database Indexing, Change Data Capture (CDC) · sdcourse — Log Format Normalization and Serialization, Faceted Search and Multi-Dimensional Filtering

Summary: Luc's angle is the OLTP database deciding what to pre-organize so future reads are cheap — an index, or a change stream tapped off the transaction log. sdcourse's angle is the log pipeline doing the identical trick on a different substrate — normalizing formats and pre-building inverted indexes so a billion-log search doesn't turn into a full scan. Same move, two systems.

Luc's Lens: Pre-Paying for Reads, Whether the Data Is at Rest or in Motion
Luc's starting point is that indexing is a reflex, not a decision, and reflexes are where trouble hides. "Slow queries have a reflex fix: add an index. It works often enough that teams keep doing it; until write latency creeps up, storage balloons, and the query planner starts making strange choices." The reflex works often enough to become habit, which is exactly why it needs correcting: every INSERT, UPDATE, and DELETE has to update every index on that table too, so each index is a standing write tax, paid on every future write, in exchange for cheaper reads today. B-trees are the safe default for most OLTP access patterns — equality filters, range filters, ordered reads — but "safe default" is not the same as "free." Luc is also blunt that an index existing doesn't mean it gets used: the query planner only takes the index path when its cost model estimates that path is cheaper than a table scan, and if the table's statistics are stale, that estimate can simply be wrong, silently. Knowing when to remove an index matters as much as knowing when to add one — rarely-used indexes, duplicate indexes, low-selectivity predicates, write-heavy tables, and columns wrapped in functions (which block index use entirely) are all candidates for deletion, not just addition.

Change Data Capture is Luc's second half of the same move, applied to a stream instead of a lookup. CDC taps into the transaction log the database already keeps for durability and crash recovery, and turns every insert, update, and delete into an event other systems can react to within seconds. Of the three capture methods — timestamp polling, database triggers, and log-based capture — log-based capture is "the modern standard" because it's low-latency, minimally invasive to the source database, and preserves exact write order, where polling silently misses hard deletes and triggers add write-path overhead. But CDC is not a free real-time button: it demands idempotent consumers (because log-based delivery is generally at-least-once) and real observability into consumer lag, offsets, and dead-letter queues, or a stalled consumer becomes an invisible correctness bug. CDC also captures the fact that a row changed, not why — it is not an audit trail by default, and treating it as one is a category error. Luc's guidance: use CDC when the dataset is large but the daily delta is small and freshness genuinely matters — live dashboards, personalization, fraud detection — and skip it for append-only feeds, small tolerant-SLA datasets, or strict historical auditing, where the machinery costs more than the freshness is worth.

Decision Rule (Luc): Before adding an index, name the exact predicate it serves and verify with a real query plan that the optimizer actually chooses it — don't index on reflex, and periodically audit for indexes that are rarely used, duplicated, low-selectivity, or sitting on a write-heavy table, because those are pure write tax with no read payoff. Before adopting CDC, name the fraction of the dataset that changes daily and whether fresh data changes a real decision — if the delta is tiny and freshness matters (fraud, personalization, live dashboards), tap the transaction log; if the data is append-only, small, or the requirement is a durable audit trail, CDC is the wrong tool wearing a real-time costume. When NOT to use either: don't index "just in case," and don't wire up CDC because streaming sounds more modern than batch — "start small, capture what truly benefits from real-time data, prove the value, and expand gradually."

Luc: "Indexes are best understood as a trade: you spend extra work on writes so reads can skip unnecessary work. Once you see that trade clearly, index tuning stops feeling like superstition and starts feeling like engineering."

sdcourse's Lens: Pre-Paying for Reads in the Log Pipeline Itself
sdcourse's log format normalization problem is the pipeline-side mirror of Luc's indexing trade-off: instead of choosing between "index everything" and "index nothing," the choice is between "force every producer onto one format" (politically impossible, technically disruptive) and "build a custom converter for every producer-consumer pair," which is N×M complexity that explodes as sources multiply. The fix is the same shape as an index — do the structuring work once, up front, so every future read is cheap. Converting every incoming format to a canonical intermediate representation first turns N×M direct converters into O(N) — one parser and one serializer per format — and sdcourse names this explicitly as decoupling: "Format normalization is a form of decoupling. Just as message queues decouple producers from consumers in time, format normalization decouples them in representation. This decoupling enables independent evolution — your analytics team can switch from JSON to Avro without coordinating with every upstream producer." Naive conversion handles about 5,000 logs/second per core; layering in object pooling, buffer management, batch processing, parallel conversion, and zero-copy passthrough pushes that past 50,000/second, at which point the bottleneck stops being CPU and becomes memory bandwidth. Production systems avoid guessing at format by trusting Content-Type headers when present, falling back to magic bytes for binary formats, and using heuristics only for text-based formats as a last resort.

Faceted search is the read-side payoff of that up-front structuring, and it is functionally an index built for a different kind of query: "Traditional search requires knowing exactly what you're looking for. Faceted search flips this — it shows you what's available to explore." The mechanism is an inverted index mapping each facet value to matching document IDs, which costs 30-40% additional storage but converts an O(n) full scan into an O(k) lookup — for 1 billion logs, a 10-minute scan becomes a 50ms index lookup. That's Luc's write-tax-for-read-speed trade again, just quantified on the log side: "Inverted indexes map each facet value to document IDs... this transforms a 10-minute scan into a 50ms index lookup. The cost: write amplification. Each log ingestion updates multiple indexes — one per facet." sdcourse also names a concrete anti-pattern — caching final search results per user query, rather than caching aggregations at the dimension level (counts per facet) — and a routing strategy: filter-first when a filter is selective (under 5% of docs), aggregate-first when it's broad (over 50% of docs). At the storage layer, representing 1 million matching document IDs as a sorted integer array costs 4MB, while a compressed bitmap does the same job in 50KB with O(1) intersection. Splunk caps facets at 10,000 unique values per day to keep cardinality bounded; Netflix's cardinality-aware query planning cut search P99 latency from 8 seconds to 400ms.

Table — Metric / Value / Why it matters:
- Direct converter complexity: N×M pairs. What canonical-format normalization replaces.
- Canonical-format complexity: O(N). One parser + one serializer per format instead.
- Naive conversion throughput: ~5,000 logs/sec/core. Baseline before optimization.
- Optimized conversion throughput: 50,000+ logs/sec. Pooling, batching, parallelism, zero-copy passthrough.
- Inverted index storage overhead: 30-40% extra. Cost of turning O(n) scans into O(k) lookups.
- 1B-log facet scan, unindexed vs. indexed: 10 min → 50ms. The concrete payoff of the storage overhead above.
- 1M doc IDs: sorted array vs. compressed bitmap: 4MB vs. 50KB. Bitmap gives O(1) intersection at a fraction of the size.
- Netflix search P99 latency: 8s → 400ms. Cardinality-aware query planning in production.

Production Reality: The anti-pattern here has the same shape as Luc's stale-statistics warning: caching final results per user query looks like it should help, but log queries have too much combinatorial variety in their filter combinations for full-result caching to get meaningful hit rates, so the cache mostly misses while still paying its maintenance cost. Caching at the dimension level — counts per facet — reuses across the many different filter combinations users actually issue, the same way a well-chosen index serves many different WHERE clauses instead of one. And write amplification is not a side effect to tolerate quietly: every log ingestion updates one inverted-index entry per facet, so a facet schema chosen carelessly multiplies write cost across every single ingested log, forever, exactly like an over-indexed OLTP table.

sdcourse: "When your system generates millions of logs per hour, finding relevant information becomes like searching for a needle in a haystack. Traditional search requires knowing exactly what you're looking for. Faceted search flips this - it shows you what's available to explore."

Diagram callout: Luc's index and sdcourse's inverted index are the same bet made twice: pay a write cost now so a future read doesn't have to scan everything. (LUC box: Structure the Row Store — Index = write tax for read speed. CDC taps the transaction log — small delta, real freshness need, idempotent consumers required. SDCOURSE box: Structure the Log Stream — Canonical format: O(N) not N×M. Inverted index: 30-40% storage tax, 10min scan becomes 50ms lookup — same trade, different substrate.)

Where They Converge / Diverge:
Converge: Both are describing the identical trade — do structuring work up front, on every write, so a specific future read pattern becomes cheap instead of a full scan; Luc's B-tree index and sdcourse's inverted index both cost storage and write amplification, and both only pay off if the read pattern they were built for actually happens.
Diverge: Luc's structuring targets a single OLTP row store answering point and range queries, and CDC targets exporting that store's changes outward as a stream for other systems to consume; sdcourse's structuring targets a distributed log pipeline ingesting from many heterogeneous producers and answering exploratory, multi-dimensional facet queries over billions of events. Luc worries about the optimizer choosing not to use an index because statistics are stale; sdcourse worries about write amplification across many facets at ingestion-time scale and about caching at the wrong granularity. A team can get Luc's OLTP indexing exactly right and still watch their log-search product time out, because faceted search over a billion-event stream is a different structuring problem with its own index (inverted, bitmap-compressed) and its own anti-pattern (per-query result caching instead of per-dimension aggregation caching).

Active Recall questions posed in the chapter:
Q1. Per Luc, why can an index exist on a table and still never be used by the query planner, and what two conditions does Luc give for when CDC is worth adopting versus when it's the wrong tool?
Q2. Per sdcourse, why does canonical-format normalization reduce N×M converters to O(N), and what specific anti-pattern turns faceted-search caching into a low-hit-rate cost center?
Q3. Luc's index and CDC operate on a single OLTP database; sdcourse's format normalization and inverted facet index operate on a distributed log pipeline. Using the write-amplification concept from both lenses, explain why "structure data now so retrieval is fast later" produces a different failure mode in each system.`,
  },
  {
    id: 5,
    title: 'Tiered Storage & Caching Economics',
    content: `Sources: lucsystemdesign — Database Caching Strategies, Connection Pooling · sdcourse — Distributed Log Storage and Tiered Architecture

Summary: Luc's angle is the decision framework: which caching strategy, and how many pooled connections, does this workload actually need. sdcourse's angle is that same question scaled to a distributed log pipeline, where the answer becomes a physical hot/warm/cold tier assignment for every byte you store. Same underlying question — where does this data live, and at what cost — asked at two different altitudes.

Luc's Lens: Deciding What Lives Close and What Waits
Luc treats caching as a correctness decision wearing a performance-optimization costume. "Caching is not just a performance optimization. It is part of your system's correctness model." Done poorly, it introduces stale reads, hidden consistency bugs, and memory waste that only shows up in production — the bug doesn't announce itself at cache-miss time, it waits for an eviction, a deployment, or an incident to expose it. Luc lays out five named strategies, each trading consistency for speed differently: Cache-Aside (application checks cache first, falls through to DB on miss, then populates the cache itself), Write-Through (cache and database updated synchronously on every write — strong consistency, higher write latency, possible cache pollution), Write-Behind/Write-Back (cache updated first, database flushed later in the background — fast writes and high throughput, but data loss risk if the cache node crashes before the flush), Read-Through (the cache itself owns the miss-fetch from the DB, giving cleaner application code at the cost of a cold-start penalty), and Write-Around (writes bypass the cache entirely and go straight to the database, with data entering cache only on a later read). None of these is universally correct; the choice has to be driven by read-vs-write ratio, consistency requirements, and how much operational complexity the team can actually own.

Connection pooling is Luc's second half of the same "what stays warm and ready vs. what gets fetched cold" argument, just applied to database connections instead of query results. Every fresh connection to a database pays a TCP handshake, TLS negotiation, and authentication round trip before a single query can run — without pooling, every request starts cold, and that repeated cold-start tax shows up as extra latency, server strain, connection churn, and eventual throughput collapse under load. A pool manages the creation, checkout, release, validation, and cleanup of a standing set of connections so that cost is paid once and amortized, not paid per request. But sizing the pool is its own decision problem, structurally identical to picking a caching strategy: oversized pools can quietly throttle the database's own capacity, while undersized pools leave threads waiting on a connection instead of serving users — and a healthy pool can even mask a deeper problem, since queries that are actually maxing out CPU or I/O still create bottlenecks no amount of pooling fixes. The target isn't "as many connections as possible," it's exactly enough to keep the system steady at peak efficiency.

Decision Rule (Luc): Pick a caching strategy by naming the read/write ratio and the consistency budget first, not by reaching for whichever one is easiest to bolt on: strong consistency and tolerable write latency point to Write-Through; high write throughput with an accepted small data-loss window points to Write-Behind; simple application code with an accepted cold-start cost points to Read-Through; a write-heavy path that's rarely re-read points to Write-Around. Size a connection pool the same way — against measured peak concurrency, not intuition — and treat "the pool is healthy" as no proof that the underlying queries are cheap; check CPU and I/O separately. In both cases: "Match your caching strategy to your access patterns, failure tolerance, and consistency needs; and your system will scale calmly instead of nervously."

Luc: "Caching is not just a performance optimization. It is part of your system's correctness model."

sdcourse's Lens: Hot, Warm, Cold — Caching's Decision Framework at Storage Scale
sdcourse's tiered architecture is Luc's caching decision applied to an entire storage system rather than a single lookup path. "Most engineers think log storage is solved by 'just use Elasticsearch' or 'dump everything to S3,' but the real complexity emerges when you need sub-second query performance on historical data while maintaining cost-effective storage for compliance retention." The resolution is a three-tier storage design: Hot (Redis, sub-millisecond, last 24h) → Warm (PostgreSQL, sub-second, 30 days) → Cold (file-based, cost-optimized, compliance retention). That's a physical, per-byte version of Luc's cache-strategy choice — Hot tier behaves like an aggressively warmed cache tuned for latency, Cold tier behaves like Luc's Write-Around: data that isn't worth keeping close because it's rarely re-read, only retained because something (compliance) requires it to exist somewhere. sdcourse is explicit that age alone is the wrong axis to tier on: "The key insight: storage tier decisions should be driven by business value, not just age." A log that's two years old but tied to an active compliance investigation may need to move back toward the warm tier regardless of its timestamp — the tiering logic has to be adaptive to value, not a fixed TTL clock.

That adaptivity has a measured payoff: adaptive rotation reduces storage costs by 60-70% compared to naive time-based rotation, because naive rotation keeps paying hot-tier prices for data nobody is querying anymore. The mirror-image failure mode is a caching problem in the Luc sense, not a storage problem: cache hit ratio below 85% indicates either wrong data being cached or TTL too aggressive — which is precisely Luc's warning that the wrong caching strategy quietly accumulates risk rather than announcing itself. And sdcourse flags a specific operational trap unique to this domain: the monitoring system watching the tiered storage pipeline can itself become the largest log producer. "The monitoring system often generates more log data than the applications it's monitoring. This recursive complexity requires careful design to avoid monitoring loops and resource exhaustion." A tiering and caching layer that doesn't account for its own observability traffic can end up filling its hot tier with metrics about the hot tier.

Table — Metric / Value / Why it matters:
- Hot tier: Redis, sub-millisecond, last 24h. Aggressively warmed, latency-optimized — Luc's Read-/Write-Through territory.
- Warm tier: PostgreSQL, sub-second, 30 days. Middle ground: still queryable, not free.
- Cold tier: File-based, cost-optimized, compliance retention. Rarely re-read, kept because required — Luc's Write-Around analog.
- Adaptive vs. naive time-based rotation: 60-70% storage cost reduction. Payoff of tiering by business value, not just age.
- Cache hit ratio floor: Below 85%. Signals wrong data cached or TTL too aggressive.

Production Reality: The same wrong-strategy risk Luc describes for application caches shows up here as a hit-ratio number you can actually watch: a cache hit ratio dropping below 85% is the tiered-storage equivalent of Luc's "quietly accumulates risk until a cache eviction, deployment, or incident exposes it" — except here it's directly measurable, so there's no excuse for it to stay hidden. The monitoring-loop trap is the sharper production reality: a tiering system has to budget hot-tier capacity for its own telemetry, or the system meant to keep storage costs down becomes the thing inflating them, consuming the same sub-millisecond Redis capacity it was supposed to be protecting for real query traffic.

sdcourse: "The key insight: storage tier decisions should be driven by business value, not just age."

Diagram callout: Luc's caching-strategy choice and sdcourse's hot/warm/cold tier are the same "what stays close, what waits" decision — one made per query, one made per byte at storage scale. (LUC box: Pick the Strategy — 5 caching strategies, sized by read/write ratio + consistency need. Pool connections to just enough, not as many as possible. SDCOURSE box: Assign the Tier — Hot/Warm/Cold by business value, not age — 60-70% cost cut vs. naive. Hit ratio below 85% = wrong data cached or TTL too aggressive.)

Where They Converge / Diverge:
Converge: Both frameworks reject a single default: Luc insists the caching strategy must match access pattern, consistency needs, and failure tolerance rather than being picked by habit, and sdcourse insists tier placement must be driven by business value rather than by age alone — both are "decide deliberately or the wrong choice will quietly cost you" arguments, and both name a measurable early-warning signal (Luc's masked CPU/I/O bottleneck behind a "healthy" pool; sdcourse's sub-85% hit ratio) for when the choice has already gone wrong.
Diverge: Luc's unit of decision is a single cache or a single connection pool serving one service's access pattern; sdcourse's unit of decision is an entire storage system's worth of data, physically routed across three distinct storage engines (Redis, PostgreSQL, file-based) with different durability and compliance guarantees. Luc's failure mode is stale reads or a pool that silently throttles the database; sdcourse's failure mode is a monitoring system that recursively floods its own hot tier with telemetry about itself — a problem that has no equivalent at the single-cache scale Luc is describing, because it only emerges once you're operating a whole tiered pipeline with its own observability surface.

Active Recall questions posed in the chapter:
Q1. Per Luc, name the five caching strategies and the one factor he says should never be the deciding one for connection pool sizing (i.e., what is the actual sizing target instead of "as many connections as possible")?
Q2. Per sdcourse, what are the three storage tiers and their latency/retention characteristics, and what specific hit-ratio number signals that a tier's caching is misconfigured?
Q3. Luc's caching-strategy decision operates on a single cache serving one access pattern; sdcourse's hot/warm/cold tiering operates on a whole storage system with its own observability traffic. Explain why the "monitoring system generates more log data than the applications it's monitoring" failure has no direct equivalent at Luc's single-cache scale.`,
  },
  {
    id: 6,
    title: 'Fast Access: Redis, Consistent Hashing & Bloom Filters',
    content: `Sources: lucsystemdesign — Redis, Consistent Hashing, Bloom Filters · sdcourse — Bloom Filters in Log Processing, Distributed Query Engine and Caching Patterns

Summary: Both authors independently reach for the same trick: before you pay full price for an answer, ask a cheap, approximate gatekeeper first. Luc names the general-purpose toolkit — an in-RAM store, a stable way to spread keys across it, and a probabilistic filter that says "definitely not" for free. sdcourse shows what happens when that toolkit is wired into one real, high-volume pipeline: exact latency numbers, exact hit-ratio floors, exact TTLs.

Luc's Lens: RAM, a Ring, and a Bit Array — Three Ways to Skip Work
Luc's Redis section starts from a correction, not a feature list: Redis is not a general-purpose database replacement, it's a performance layer that solves specific problems extremely well. Everything is stored in RAM as key-value pairs, but the values support richer structures than a plain cache would need — Strings, Hashes, Lists, Sets, and Sorted Sets. A structural detail does a lot of Luc's explanatory work: Redis uses a single-threaded event loop, meaning one command executes at a time, which avoids locking and keeps operations atomic without the coordination overhead a multi-threaded store would need. But the same section is just as clear about when Redis is the wrong tool: don't reach for it when the dataset is large and cold (RAM is expensive), when you need complex queries, when you need strong durability (financial transactions, medical records), or when the workload is stateless and simple enough that a cache buys nothing. "The problem often isn't the database itself. It's that you're asking it to answer the same questions, over and over, thousands of times a second" — Redis exists to absorb that repetition, not to replace the database being asked.

Consistent hashing is Luc's answer to a different question: once you've decided to spread keys across multiple Redis (or cache, or shard) nodes, how do you keep that mapping stable as nodes come and go? Naive hashing — shard = hash(key) % N — looks simple until N changes: the moment a node is added or removed, the entire mapping shifts with it, causing a full cache reset. Consistent hashing fixes this by mapping both keys and servers into the same hash space, a ring, and walking clockwise from a key's position until you hit the first server. When a node is added or removed, only the keys between the new position and the previous node need to move; everything else stays exactly where it was. In practice that means when a cluster grows, only about 1/N of the keys move, so caches stay warm and rebalancing is light — and multiple virtual nodes per physical server spread that load more evenly across the ring. Bloom filters close out Luc's trio by attacking a different kind of waste entirely: most systems spend more time proving what isn't there than what is — every cache miss, every 404, every "not found" query costs real CPU, I/O, and bandwidth. A Bloom filter answers "could this exist?" using a bit array and multiple hash functions, without storing the item itself. It never gives false negatives — if you inserted it, it will always return "maybe" — but it can give false positives; if any queried bit is 0 the item definitely doesn't exist, and if all are 1 it might exist. The false positive rate is tunable by the number of hash functions, and Luc is explicit about where not to use one: exact answers (billing, access control, authentication), frequent deletions, or unpredictably growing data.

Decision Rule (Luc): Reach for Redis when the same question is being asked repeatedly and RAM cost is justified by request volume — not as a default data layer. Once you're sharding that cache (or any keyed store) across multiple nodes, use consistent hashing instead of modulo hashing the moment node count is expected to change, because consistent hashing trades perfect balance for predictable, bounded churn: only ~1/N of keys move per topology change, not all of them. Put a Bloom filter in front of any expensive "does this exist?" check with a high miss rate — it can only ever save you a lookup (definite no) or cost you one wasted check (false positive maybe), never return a wrong "yes" for something absent. None of the three replace the system of record; all three exist to reduce how often that system of record gets asked.

Luc: "Redis is best understood as a performance multiplier, not a database replacement. Used correctly, Redis turns slow paths into fast ones and fragile systems into responsive ones. Used blindly, it becomes an expensive, leaky abstraction."

sdcourse's Lens: The Same Gatekeeper, Wired Into a Log Pipeline
sdcourse's Bloom filter section is Luc's "definitely not / probably present" idea with the numbers attached. In log processing, a Bloom filter answers "definitely not present" or "probably present" — zero false negatives, tunable false positives typically in the 1-5% range — and the payoff is concrete: without a Bloom filter, an existence query costs 50-200ms; with one, it costs 0.1-1ms, alongside a roughly 95% memory reduction compared to hash-based lookups. sdcourse treats this as more than a speed trick: "Bloom filters transform expensive 'does this exist?' questions into instant responses with minimal memory overhead. They're not just performance optimizations - they're architectural game-changers that enable entirely new query patterns in distributed systems." The operational detail that separates this from Luc's general description is scope discipline — different log types (errors, access logs, security events) each maintain their own separate Bloom filter, rather than one shared filter across categories, because the acceptable false-positive cost differs by log type and mixing them would blur that tuning. The asymmetric payoff is the same logic Luc describes, restated for a pipeline: "if bloom filter says 'error might exist,' you can check the actual storage. But if it says 'error definitely doesn't exist,' you save an expensive lookup entirely."

The fast-access half of sdcourse's caching section is where consistent hashing's underlying goal — spread load across nodes without a full reshuffle on every topology change — shows up as a concrete Redis deployment rather than an abstract ring. Rather than one flat TTL for everything, the layer is split by how fast each kind of result goes stale: query results sit for 5 minutes, rolled-up aggregations get a full hour since they drift slowly, and the most recent 15 minutes of hot data is refreshed every 30 seconds because that window churns the fastest. Because log queries exhibit strong temporal locality, cache hit ratios above 95% are achievable with this tiering — the same "ask the fast layer first" instinct behind both Redis and Bloom filters, just measured as a hit-ratio percentage instead of a latency number. sdcourse is equally blunt about a failure mode unique to this speed and scale: synchronously updating the cache on every write collapses under high-velocity log ingestion, since the invalidation work piles up on the hot path and turns any partial failure into a consistency mess rather than a clean retry — a warning that rhymes with Luc's own list of when not to reach for Redis (strong durability needs, complex queries) even though the two lists don't overlap term-for-term.

Table — Mechanism / Value / Why it matters:
- Bloom filter query time without filter: 50-200ms. Cost of a raw existence check against storage.
- Bloom filter query time with filter: 0.1-1ms. Sub-millisecond target once the filter screens the request.
- Bloom filter memory reduction: ~95% vs. hash-based lookups. Bit array is far cheaper than storing full keys.
- Bloom filter false positive rate: Configurable, typically 1-5%. Tunable cost of the "maybe" answer.
- Query result cache TTL: 5 minutes. Top tier of the three-tier Redis scheme.
- Hot data cache TTL: 30 seconds, last 15 min. Shortest TTL, covers the highest-churn recent window.
- Achievable cache hit ratio: >95%. Driven by temporal locality — most log queries hit recent data.

Production Reality: Separate Bloom filters per log type is the detail a general description of the data structure would never surface: it exists because a single shared filter would force every log category into the same false-positive tolerance, when in practice a security-event filter and an access-log filter can justify very different tuning. And the write-through anti-pattern is what happens when a team applies Luc's Redis caching instinct without his own "when NOT to use Redis" caveat about complex, high-durability workloads — high-velocity log writes plus synchronous cache invalidation is exactly the kind of workload where the coordination cost swamps the benefit.

sdcourse: "Key Insight: False positives are acceptable in many log processing scenarios. If bloom filter says 'error might exist,' you can check the actual storage. But if it says 'error definitely doesn't exist,' you save an expensive lookup entirely."

Diagram callout: Luc names the gatekeeper pattern once, generically; sdcourse deploys all three tools — fast store, spread load, cheap "no" — inside one log pipeline with numbers attached to each. (LUC box: Three General Tools — Redis for repeated questions, consistent hashing so only ~1/N of keys move, Bloom filter to skip proving absence. SDCOURSE box: One Wired Pipeline — Bloom filter: 50-200ms to 0.1-1ms, 95% memory saved, per log type. 3-tier Redis TTLs, >95% hit ratio, never write-through.)

Where They Converge / Diverge:
Converge: Bloom filters are the clean 1:1 match — both authors describe the identical mechanism (bit array, multiple hash functions, zero false negatives, tunable false positives) and reach the same conclusion in nearly the same words: Luc says a fast "maybe" is all you need when most of your system's time goes to proving nothing exists; sdcourse says the exact same trade pays off as a 50-200ms-to-0.1-1ms latency win. Both also treat "ask cheap before you ask expensive" as the underlying principle behind Redis/consistent hashing and the three-tier cache alike, not just behind Bloom filters specifically.
Diverge: Luc's three tools stay general-purpose and independent — Redis, consistent hashing, and Bloom filters are each introduced with their own "when NOT to use" list, as building blocks a reader picks among per problem. sdcourse fuses two of those same tools into one concrete deployment: a three-tier Redis TTL scheme (the caching half) sitting alongside per-log-type Bloom filters (the existence-check half), inside a single system where the exact numbers — TTL values, hit-ratio floor, memory reduction percentage — are the point, not the general mechanism. Luc never quotes a specific latency number for Redis or a specific 1/N fraction beyond "about"; sdcourse's value only exists once bolted into a real pipeline with SLAs attached.

Active Recall questions posed in the chapter:
Q1. Per Luc, why does Redis's single-threaded event loop avoid the need for locking, and what four conditions does he give for when NOT to reach for Redis?
Q2. Per sdcourse, what is the measured latency swing a Bloom filter produces on an existence query (with numbers), and why does the pipeline maintain a separate Bloom filter per log type instead of one shared filter?
Q3. Bloom filters are the one topic both authors describe almost identically. Using consistent hashing (Luc) and the three-tier Redis TTL scheme (sdcourse) as evidence, explain how the two authors diverge once the topic moves from "what is this data structure" to "how do I deploy fast-access tools at scale."`,
  },
]

// Per-chapter source summaries used to prompt the examiners' question generation.
// Phase tasks append entries keyed by chapter id.
const KNOWLEDGE_BY_CHAPTER = {
  1: {
    luc: 'System Design Quality Attributes (.claude/agents/lucsystemdesign.md:74-84): attributes vs pillars vs tactics; you cannot maximize everything simultaneously; vague targets like "highly available" are not falsifiable — use attribute scenarios instead.',
    sdcourse: 'Course Structure and Curriculum Design (.claude/agents/sdcourse.md:33-50): the gap between knowing system design for an interview and building a production system that survives it ("the map vs the shovel"); 254-lesson/270-day LogStream curriculum; Discord activity is the best predictor of completion.',
  },
  2: {
    luc: 'CAP Theorem (.claude/agents/lucsystemdesign.md:317-329): "pick two of three" is misleading — the trade-off only appears when the network splits; CP vs AP framed as "wrong data vs no data." ACID vs BASE (:422-431): same fork at the data-model layer. Strong vs Eventual Consistency (:290-299): same fork at the read-path layer, plus the CAP-consistency vs ACID-consistency distinction.',
    sdcourse: 'Multi-Region Replication and Distributed Consistency (.claude/agents/sdcourse.md:217-235): network partitions are inevitable, zero replication lag is impossible; active-active multi-region for log systems; MirrorMaker 2 adds 50-200ms; alert threshold of >10s replication lag against RPO budget; vector clocks over physical timestamps.',
  },
  3: {
    luc: 'Database Selection (.claude/agents/lucsystemdesign.md:30-45): choosing a database is a "question problem" not a schema problem — pick the store built for your hardest recurring question; primary-plus-secondary pattern. SQL vs NoSQL (:359-367): schema/consistency/complexity vs flexibility/horizontal-scale/speed trade-off.',
    sdcourse: 'Distributed Query Engine and Caching Patterns (.claude/agents/sdcourse.md:236-250): CQRS separates write (Kafka ingestion) from read (pre-computed aggregations) for ~10x query capacity at a 100-500ms staleness cost; anti-pattern warning against write-through caching for high-velocity log data; three-tier Redis TTL scheme (5min/1hr/30s); naive log tables fail past 10M records.',
  },
  4: {
    luc: 'Database Indexing (.claude/agents/lucsystemdesign.md:488-497): indexing as a write-tax-for-read-speed trade, not a reflex; query planner may silently skip a stale-statistics index; when to remove an index. Change Data Capture (CDC) (:178-188): taps the transaction log; log-based capture is the modern standard over polling/triggers; requires idempotent consumers; not an audit trail.',
    sdcourse: 'Log Format Normalization and Serialization (.claude/agents/sdcourse.md:333-347): canonical intermediate format turns N×M converters into O(N); 5,000 to 50,000+ logs/sec/core with optimization. Faceted Search and Multi-Dimensional Filtering (:317-332): inverted index turns a 10-minute scan into a 50ms lookup at 30-40% storage overhead; per-dimension aggregation caching over per-query result caching.',
  },
  5: {
    luc: 'Database Caching Strategies (.claude/agents/lucsystemdesign.md:244-255): caching as part of the correctness model, not just performance; five strategies (Cache-Aside, Write-Through, Write-Behind, Read-Through, Write-Around) chosen by read/write ratio and consistency needs. Connection Pooling (:169-177): pools amortize TCP/TLS/auth cold-start cost; sizing target is peak efficiency, not maximum count; a healthy pool can mask CPU/I/O bottlenecks.',
    sdcourse: 'Distributed Log Storage and Tiered Architecture (.claude/agents/sdcourse.md:143-157): three-tier storage — Hot (Redis, sub-ms, 24h), Warm (PostgreSQL, sub-sec, 30 days), Cold (file-based, compliance); tier by business value not age, 60-70% cost reduction vs. naive rotation; cache hit ratio below 85% signals misconfiguration; monitoring can become the largest log producer.',
  },
  6: {
    luc: 'Redis (.claude/agents/lucsystemdesign.md:310-316): a performance layer, not a database replacement; single-threaded event loop avoids locking; when NOT to use it (large/cold data, complex queries, strong durability, stateless simple workloads). Consistent Hashing (:200-210): ring-based mapping means only ~1/N keys move per topology change, vs. a full reset under modulo hashing. Bloom Filters (:211-220): bit array + hash functions answer "could this exist?" with zero false negatives, tunable false positives; wrong for exact answers, frequent deletions, or unpredictable growth.',
    sdcourse: 'Bloom Filters in Log Processing (.claude/agents/sdcourse.md:301-316): existence checks drop from 50-200ms to 0.1-1ms with ~95% memory reduction and 1-5% false positive rate; separate filter per log type (errors/access/security) rather than one shared filter. Distributed Query Engine and Caching Patterns (:236-250, reused from Chapter 3 with the fast-access/in-memory-hashing angle): three-tier Redis TTLs (5min/1hr/30s) achieve >95% hit ratio; never write-through under high-velocity ingestion.',
  },
}

const QUESTION_SCHEMA = {
  type: 'object',
  properties: {
    questions: { type: 'array', items: { type: 'string' }, minItems: 5, maxItems: 5 },
  },
  required: ['questions'],
}

const ANSWER_SCHEMA = {
  type: 'object',
  properties: {
    answers: { type: 'array', items: { type: 'string' } },
  },
  required: ['answers'],
}

const AUDIT_SCHEMA = {
  type: 'object',
  properties: {
    confusionLog: { type: 'array', items: { type: 'string' } },
    improvements: { type: 'array', items: { type: 'string' } },
    blockers: { type: 'array', items: { type: 'string' } },
  },
  required: ['confusionLog', 'improvements', 'blockers'],
}

const SCORE_SCHEMA = {
  type: 'object',
  properties: {
    accuracy: { type: 'number' },
    coverage: { type: 'number' },
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['accuracy', 'coverage', 'gaps'],
}

const SIGNOFF_SCHEMA = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' },
    notes: { type: 'array', items: { type: 'string' } },
  },
  required: ['pass', 'notes'],
}

// NOTE: the Workflow `args` global arrives EMPTY in this environment (a known
// gotcha — a passed object silently becomes {}, same as the STORM engine's
// documented workaround). So chapterIds is NOT read from `args`; the controller
// writes it to this fixed run-config file before invoking the workflow, and this
// setup step reads it via an agent (scripts have no filesystem access).
const RUN_CFG = '/Users/syedamberiqbal/Documents/workspace/Claude_Code/SOIC_Scraper/.claude/worktrees/heuristic-mclaren-37718f/output/sdcourse_luc/_run.json'
const runCfg = await agent(
  `Read the JSON file at ${RUN_CFG} and report its exact contents.`,
  { schema: { type: 'object', properties: { chapterIds: { type: 'array', items: { type: 'integer' } } }, required: ['chapterIds'] }, label: 'read-run-cfg' }
)
const chapterIds = runCfg.chapterIds
const chapters = CHAPTERS.filter(c => chapterIds.includes(c.id))

if (chapters.length !== chapterIds.length) {
  throw new Error(`Requested chapterIds ${JSON.stringify(chapterIds)} but CHAPTERS only has ${CHAPTERS.map(c => c.id)}`)
}

phase('Questions')
const results = await pipeline(
  chapters,
  async (chapter) => {
    const know = KNOWLEDGE_BY_CHAPTER[chapter.id]
    const [lucQ, sdQ] = await parallel([
      () => agent(
        `Generate 5 examination questions about your (Luc's) lens in this chapter. Source material: ${know.luc}\n\nRules: at least 2 trade-off questions, at least 1 "when NOT to use" or precise-term question, at least 1 WHY question.`,
        { agentType: 'lucsystemdesign', phase: 'Questions', schema: QUESTION_SCHEMA, label: `luc-q-ch${chapter.id}` }
      ),
      () => agent(
        `Generate 5 examination questions about your (sdcourse's) lens in this chapter. Source material: ${know.sdcourse}\n\nRules: at least 2 trade-off questions, at least 1 precise numeric-benchmark question, at least 1 WHY question.`,
        { agentType: 'sdcourse', phase: 'Questions', schema: QUESTION_SCHEMA, label: `sd-q-ch${chapter.id}` }
      ),
    ])
    return { chapter, lucQ, sdQ }
  },
  async ({ chapter, lucQ, sdQ }) => {
    phase('AnswerAudit')
    const allQuestions = [...lucQ.questions, ...sdQ.questions]
    const [answers, audit] = await parallel([
      () => agent(
        `You are a student who has read ONLY this chapter (no outside knowledge). Chapter content:\n\n${chapter.content}\n\nAnswer each question using only the chapter content. Questions:\n${allQuestions.map((q, i) => `${i + 1}. ${q}`).join('\n')}`,
        { agentType: 'justin-sung', phase: 'AnswerAudit', schema: ANSWER_SCHEMA, label: `answers-ch${chapter.id}` }
      ),
      () => agent(
        `Read this chapter as Alex (a curious 15-year-old with no domain background) and produce a clarity audit — confusion log, additive improvement requests (DEFINE/ANALOGY/BRIDGE/DIAGRAM/EXAMPLE/SEQUENCE), and any remaining blockers. Never ask to remove content. Chapter content:\n\n${chapter.content}`,
        { agentType: 'alex', phase: 'AnswerAudit', schema: AUDIT_SCHEMA, label: `audit-ch${chapter.id}` }
      ),
    ])
    return { chapter, lucQ, sdQ, answers, audit }
  },
  async ({ chapter, lucQ, sdQ, answers, audit }) => {
    phase('Score')
    const answerText = answers.answers.join('\n')
    const [lucScore, sdScore] = await parallel([
      () => agent(
        `Score the student's answers to YOUR questions on accuracy (0-10) and coverage (0-10). Your questions:\n${lucQ.questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}\n\nStudent answers:\n${answerText}\n\nList any gaps.`,
        { agentType: 'lucsystemdesign', phase: 'Score', schema: SCORE_SCHEMA, label: `luc-score-ch${chapter.id}` }
      ),
      () => agent(
        `Score the student's answers to YOUR questions on accuracy (0-10) and coverage (0-10). Your questions:\n${sdQ.questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}\n\nStudent answers:\n${answerText}\n\nList any gaps.`,
        { agentType: 'sdcourse', phase: 'Score', schema: SCORE_SCHEMA, label: `sd-score-ch${chapter.id}` }
      ),
    ])
    const pass = lucScore.accuracy >= 9.0 && lucScore.coverage >= 9.0 && sdScore.accuracy >= 9.0 && sdScore.coverage >= 9.0
    return { chapterId: chapter.id, title: chapter.title, lucScore, sdScore, audit, pass }
  }
)

const allPassed = results.every(r => r.pass)
log(`Phase pass: ${results.filter(r => r.pass).length}/${results.length} chapters at >=9.0 on all four scores`)

let signoff = null
if (allPassed) {
  phase('SignOff')
  const idsLabel = chapterIds.join(',')
  const [luc, sd, justin, alex] = await parallel([
    () => agent(`Final sign-off for chapters ${idsLabel}: confirm decision-framework accuracy and "when NOT to use" coverage are both >=9.0 across these chapters as a whole. Set pass=false if not.`, { agentType: 'lucsystemdesign', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
    () => agent(`Final sign-off for chapters ${idsLabel}: confirm production accuracy (benchmarks, failure modes, exact numbers) is >=9.0 across these chapters as a whole. Set pass=false if not.`, { agentType: 'sdcourse', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
    () => agent(`Final sign-off for chapters ${idsLabel}: confirm pedagogical quality (WHY->WHAT->HOW structure, retrieval practice, emotional framing) meets at least 6/7 criteria across these chapters. Set pass=false if not.`, { agentType: 'justin-sung', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
    () => agent(`Final sign-off for chapters ${idsLabel}: confirm there are no remaining BLOCKERS for a 15-year-old reader. Set pass=false if any blocker remains.`, { agentType: 'alex', phase: 'SignOff', schema: SIGNOFF_SCHEMA }),
  ])
  signoff = { luc, sd, justin, alex, allPassed: [luc, sd, justin, alex].every(Boolean) && [luc, sd, justin, alex].every(s => s.pass) }
}

return { results, allPassed, signoff }
