<!--
ABOUTME: Draft of the Steel blog article that introduces internal-agents.com to readers.
ABOUTME: Facts come from the catalog and from docs/launch-article-research-2026-10.md; [TK] marks open inputs.
-->

# What companies learn when they build their own agents

The model is rarely what holds an internal agent back. Companies that write honestly about their agents spend most of their words on everything around it: where the agent shows up, who checks its work, when it gives up, and what survives when it crashes.

These agents are also spreading faster than anyone can measure them. When Shopify described how River works, it called its own adoption numbers "already wrong, in the upward direction."

We started paying attention for two reasons. Teams building on Steel kept asking us how other companies did it. Should the agent live in Slack or get its own tool? How many retries are enough? Who reviews its output? We didn't have good answers, partly because we were asking ourselves the same things. **[TK: one or two sentences about the agents we were building and where we got stuck.]**

So we read everything we could find. Stripe, Shopify, Uber, DoorDash, Dropbox, Databricks, Sentry, Ramp, and many others have written candidly about agents built for their own engineers, support teams, finance teams, and on-call rotations. We wrote down what each one built, how it works, and what went wrong, with a source for every claim. That became the [Internal Agents Map](https://internal-agents.com/). We built it for ourselves. It's public because the questions aren't only ours.

This is what we learned.

## What we mean by an internal agent

The vocabulary isn't settled. Google's glossary calls them "background agents" and defines them by how they run. The companies building them mostly say "internal agent" and leave it there.

We use a narrower definition: an agent that an organization builds for its own work. It keeps an identity across runs, works with the organization's context and tools, and has a clear answer to who supervises it. That last part matters more than it sounds. Most of what follows is about supervision.

We also separate the agent from the systems that support it, like session stores, sandboxes, and tool gateways. Many of the most interesting engineering posts are about the second category.

## Most of the work happens around the model

Nearly every account follows the same arc. A team gets a model doing something useful in a few weeks. The next months go into the structure around it.

DoorDash's code reviewer went through three designs. First came specialists for security, tests, and performance, which found local problems and missed changes that crossed system boundaries. Next, two generalist reviewers saw the whole change but had too much to investigate. The current design puts a scout first to write leads, and two reviewers then verify them. The model hardly changed between versions; the division of work changed every time.

Embat, a finance software company, found the same thing in customer support. Their internal agent began as one generalist. Prompt changes that helped one area made others worse, so they split it into more than ten specialists behind a router. When the router isn't sure, it asks the person. Anthropic describes something similar in its own long-running agents, separating the agent that plans, the one that builds, and the one that checks.

The teams arrived at this separately, in different domains, and it keeps recurring.

**[TK: a loop we had to redesign, or a split we made in our own agents.]**

## Agents go where people already work

Few of these agents have a home of their own. They live in Slack threads, pull requests, tickets, and CI. Shopify's River works in thousands of Slack channels. Embat's agent answers in Slack. Uber's uReview runs on every commit in CI.

This looks like a UX detail, but it shapes adoption. An agent that needs a new tab competes for attention. An agent in the thread where someone reported the bug doesn't.

## People stay in the loop, but their job changes

Most agents in the map produce a draft that a person reviews: a pull request, an investigation, a reply. Full autonomy exists, but it's narrow. It covers one decision, such as merging a change that passed every gate or downgrading a duplicate alert, never "everything the agent does."

That shifts the bottleneck to human attention, and it's the question we see most often in public discussion. Maintainers describe AI pull request volume as "overwhelming." Engineering leaders ask how to manage review load. The companies furthest along answer by filtering their own agents. Uber grades each uReview comment's confidence, removes duplicates, and suppresses categories engineers rarely act on. HubSpot puts a judge agent between its reviewer and its engineers.

Autonomy grows the same way everywhere we looked: one narrow job at a time, after the narrower version had shown it works.

## Code keeps the rules

If something must always happen, the teams that do this well don't ask the model to remember it.

Stripe describes its Minions blueprints as "a state machine that intermixes deterministic code nodes and free-flowing agent nodes." The agent decides how to fix a failing test. Linters and the push run as fixed steps. Stripe also limits how long the agent can keep trying: "We only have at most two rounds of CI," after which the branch goes back to a person, because more rounds showed "diminishing marginal returns."

Dropbox gives Nova one branch to work on, and the surrounding workflows own publishing and CI. PostHog's approval agent sits behind fixed gates. The model can be stricter than the gates but can't relax them.

The rule of thumb is easy to say and harder to follow: use the model where judgment helps, and use code wherever a rule applies.

## The conversation outlives the computer

Agents crash, time out, and get replaced. Teams that plan for this keep the work outside the process doing it.

Shopify's version is the most quotable: "Cells die, sandboxes die, machines die. The conversation doesn't." River's session is a durable, append-only log in Postgres. The workers that do the actual work are disposable, and "the harness lives outside the sandbox." Sentry's Junior pauses before its serverless deadline and queues a continuation. Sierra restores a sleeping runner by replaying events from its last checkpoint.

Each design keeps something different. A restored conversation doesn't mean the files survived, and replaying events doesn't undo what already happened in the outside world. The best accounts say exactly what their design brings back.

## Context becomes its own product

An agent is only as good as what it can see and use, and teams are investing more here than we expected.

Stripe gives Minions rule files and an internal tool server with hundreds of tools, on machines that are warmed up before a task arrives. Cloudflare found that tool descriptions alone filled much of the model's context before work started, so the agent now searches for the tool it needs. GitHub reported that its analytics agent got faster mainly because of better-curated context, not a better model.

Ramp took this furthest. Its finance agent automates work like monthly revenue reconciliation. Writing its prompts and context by hand took 30 to 45 minutes for each use, so Ramp built a second agent to do it from accountants' screen recordings. When an agent's setup becomes a job big enough to automate, the setup has become a product.

## Everyone writes their own exam

Public benchmarks can't tell you whether an agent can do your work, so teams build tests from their own history.

Databricks turns real pull requests into tasks and removes hints about the original solution. It then found tests that rejected valid alternative fixes and rewrote them by hand. A benchmark can be wrong in either direction. Anthropic reported agents passing unit tests while the feature was broken end to end, and found that a separate, skeptical evaluator worked better than asking the builder to criticize itself.

The common lesson: whoever builds shouldn't be the only one who checks, and that includes the model doing the checking.

**[TK: how we test our own agents, or what we tell clients about it.]**

## Be careful with the numbers, including ours

Almost every metric in this space is self-reported, and most of them only go up. That doesn't make them false, but it makes them easy to misread.

The best independent warning we found comes from METR. In a controlled study, experienced open-source developers using early-2025 AI tools took longer on their tasks, while believing the tools had made them faster. METR now says the result is outdated for current tools. The gap between what people feel and what is measured is the part that lasts.

So the map quotes every number exactly as published, with its date and scope, and changes nothing. When a company's own article contradicts itself, we keep both versions and say so. Read our numbers that way too.

## Failures teach the most, and they're the rarest

Launch posts report what worked. Retrospectives explain why.

Airbnb built its own agent orchestrator and never shipped it. HubSpot found that starting a Kubernetes workload for every code review added latency, cost, and operational friction, so it rebuilt the reviewer. Dropbox moved its migrations to Nova because the previous tool couldn't recover interactively when a run failed. DoorDash published two designs that didn't work before the one that did.

That's most of what we could find. Companies describe architecture freely, but rarely what an agent costs, how they evaluate it, or what they turned off. When a source doesn't say, the map records it as unknown.

## Some of this will expire

One warning applies to everything above. Anthropic put it well: "every component in a harness encodes an assumption about what the model can't do on its own." The same team removed parts of its own harness when newer models made them unnecessary.

So read these patterns as a picture of what works with today's models. Some of the structure will become unnecessary. Our guess is that new problems will take its place, but that's a guess.

## What we tell people now

When a team asks us where to start, this is roughly what we say:

- Start with work that a person can check quickly.
- Put the agent where the work already happens.
- Use code for anything that must always happen.
- Keep the record of the work outside the worker.
- Test on your own past work, and keep the checker separate from the builder.
- Decide when the agent stops before you decide how clever it is.

None of this is our invention. These teams found it, often the hard way, and wrote it down.

## What the map doesn't know yet

The map is strongest where companies publish the most, which means coding and code review. Support, finance, operations, and security are thinner, even though agents like Embat's and Ramp's show that interesting work happens there. The map also takes no position on building versus buying. It records what companies built.

Lists of AI agents already exist, but they catalog products you can buy. We couldn't find one that records what organizations built for themselves, with sources. That's the gap we're trying to fill.

## Use it, and help us fix it

The [Internal Agents Map](https://internal-agents.com/) has every agent we've studied, the source behind each claim, and short lessons on the questions above. You can browse by problem, compare designs, or export a record and work with it yourself.

If you've built an internal agent, or read about one we missed, tell us. We especially want the failures.
