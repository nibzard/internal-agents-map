<!--
ABOUTME: Draft of the Steel blog article that introduces internal-agents.com to readers.
ABOUTME: Facts come from the catalog and from docs/launch-article-research-2026-10.md; [TK] marks open inputs.
-->

# What companies learn when they build their own agents

The model is rarely what holds an internal agent back.

DoorDash rebuilt its AI code reviewer three times. The first version split the review among specialists for security, tests, and performance, and they missed changes that crossed system boundaries. The second gave the whole change to two generalist reviewers, who had too much to investigate. The third puts a scout first to write leads, and the two reviewers verify them. Each redesign changed how the work was divided and checked. ([DoorDash](https://careersatdoordash.com/blog/doordash-built-an-ai-code-reviewer-engineers-actually-listen-to/))

We kept finding versions of that story. Once an agent can produce useful work, the engineering problem becomes managing that work reliably: where the agent works, what it can see, who checks it, when it stops, and what survives when it fails.

## Why we made a map

Steel builds browser infrastructure for AI agents, so teams building agents ask us for advice. Should the agent live in Slack or get its own tool? How many retries are enough? Who reviews its output? We didn't have good answers, partly because we were asking the same questions about our own agents. **[TK: one specific thing we were building and where we got stuck. This is the most important TK in the piece.]**

So we read what companies had published about agents built for their own engineers, support teams, finance teams, and on-call rotations. For each one we recorded what it does, how it works, who supervises it, and what went wrong, with a source for every claim. That became the [Internal Agents Map](https://internal-agents.com/), which now covers dozens of organizations.

Other lists of AI agents catalog products you can buy. We couldn't find one that records, with sources, what organizations built or adapted for their own work. The map keeps company reports separate from our interpretation, preserves its sources, and marks a detail as unknown when no source covers it.

Since we sell infrastructure, you should know where we stand: we have an interest in how teams think about the systems around an agent. We've tried to report what these companies did, including where it complicates our own view.

## What we mean by an internal agent

On the map, an internal agent is an AI system that an organization builds or adapts to do work for its own teams. It works through the organization's knowledge, tools, workflows, and controls. Some work alongside a person. Others start from an event and run in the background. How closely people supervise them varies by workflow.

The map records the systems that support agents, such as session stores, sandboxes, and tool platforms, as separate [infrastructure](https://internal-agents.com/infrastructure) entries. Much of the hardest engineering in this article lives in those systems, and keeping them separate lets you compare them across companies.

## Making an agent useful

### Put it where people already work

Few of these agents have a home of their own. [Shopify's River](https://internal-agents.com/agents/shopify-river), a coding agent, works in thousands of Slack channels. Embat's internal agent, which began as a support tool for its product team, answers in Slack. [Uber's uReview](https://internal-agents.com/agents/uber-ureview) comments on code changes as part of CI.

We think this placement does a lot for adoption. An agent in the thread where someone reported the bug gets used. An agent that needs its own tab has to compete for attention.

### Divide the work

DoorDash wasn't alone in redesigning how the work is split. [Embat's agent](https://internal-agents.com/agents/embat-mr-batt) started as one generalist, and prompt changes that helped one area made others worse. Embat split it into more than ten specialists behind a router, which asks the person when it isn't sure. ([Embat](https://www.embat.io/tech/internal-ai-agent-platform)) Anthropic's long-running agents use a similar split, with one agent that plans, one that builds, and one that checks. ([Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps))

**[TK: a split or redesign we made in our own agents.]**

### Engineer the context

Teams spend more on what the agent can see and use than we expected.

Stripe gives [Minions](https://internal-agents.com/agents/stripe-minions), its coding agents, rule files and an internal tool server with hundreds of tools, on machines warmed up before a task arrives. Cloudflare measured about 15,000 tokens of tool descriptions for 34 GitLab tools before the model started any work, so its agent now searches for the tool it needs. ([Cloudflare](https://blog.cloudflare.com/internal-ai-engineering-stack/)) GitHub said its analytics agent got faster mainly because of better-curated context, with no change of model. ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-we-built-an-internal-data-analytics-agent/))

Ramp's [finance agent](https://internal-agents.com/agents/ramp-finance-agents) handles work like monthly revenue reconciliation. Writing the prompts and context for each use took 30 to 45 minutes by hand, so Ramp built a second agent that writes them from accountants' screen recordings. ([Ramp](https://ramplabs.substack.com/p/we-built-an-agent-to-prompt-our-internal))

## Making its work trustworthy

### Keep people in the loop, and protect their attention

The most common pattern in the map is an agent that produces a draft for a person to review: a pull request, an investigation, a reply. Where full autonomy exists, it usually covers one decision, such as merging a change that passed every gate or downgrading a duplicate alert.

Review then becomes the bottleneck. Maintainers of the Insight Toolkit, an open-source imaging library, described the volume of AI pull requests as overwhelming. Uber and HubSpot filter their own agents before people see the output. Uber grades each uReview comment's confidence, removes duplicates, and suppresses categories engineers rarely act on. ([Uber](https://www.uber.com/blog/ureview/)) HubSpot puts a judge agent between its code reviewer and its engineers. ([HubSpot](https://product.hubspot.com/blog/automated-code-review-the-6-month-evolution))

In the accounts that describe autonomy growing, it grew one narrow job at a time, after the narrower version had shown it worked.

### Let code keep the rules

When a step must always happen, these teams write it in code instead of asking the model to remember it.

Stripe describes its Minions blueprints as "a state machine that intermixes deterministic code nodes and free-flowing agent nodes." The agent decides how to fix a failing test, while linters and the push run as fixed steps. ([Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2))

[Dropbox's Nova](https://internal-agents.com/agents/dropbox-nova), a platform for coding agents, gives an agent one branch to work on, and the workflows around it own publishing and CI. ([Dropbox](https://dropbox.tech/machine-learning/introducing-nova-our-internal-platform-for-coding-agents)) [PostHog's StampHog](https://internal-agents.com/agents/posthog-stamphog), which approves pull requests, sits behind fixed eligibility gates. The model can be stricter than the gates but can't relax them. ([PostHog](https://github.com/PostHog/posthog/tree/988c9031bb93c74bafcdfb670c01497c79a4f644/tools/pr-approval-agent))

### Test on your own work

Public benchmarks can't tell you whether an agent can do your work, so teams build tests from their own history.

Databricks turns real pull requests into tasks. It strips out hints about the original solution, because a task that leaks the answer makes the agent look better than it is. It also found tests that rejected valid alternative fixes and rewrote them by hand, because those make the agent look worse. ([Databricks](https://www.databricks.com/blog/benchmarking-coding-agents-databricks-multi-million-line-codebase)) Anthropic saw agents pass unit tests while the feature was broken end to end, and a separate, skeptical evaluator caught more than asking the builder to criticize its own work. ([Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents))

Whoever builds the work shouldn't be the only one who checks it, and that applies to agents too.

**[TK: how we test our own agents, or what we tell clients about it.]**

## Keeping it running

### Decide when it stops

Every agent needs a rule for giving up, and the teams we read set it in different units. Stripe caps CI: "We only have at most two rounds of CI." After the second run the branch goes back to a person, because more rounds showed "diminishing marginal returns." Dropbox's Deflaker gets up to five attempts at a flaky test and carries notes from each attempt into the next.

DoorDash found that counting attempts wasn't enough. A request stuck in a loop never advanced the turn counter, and the team summed it up: "A turn counter is not a progress detector." Its reviewers now have a soft deadline, when they return what they've already verified, and a hard deadline, when they stop.

### Keep the session outside the worker

Agents crash, time out, and get replaced. Teams that plan for this keep the record of the work outside the process doing it.

Shopify puts it this way: "Cells die, sandboxes die, machines die. The conversation doesn't." Each River session is an append-only log in Postgres. The workers are disposable, and "the harness lives outside the sandbox." ([Shopify](https://shopify.engineering/under-the-river)) [Sentry's Junior](https://internal-agents.com/agents/sentry-junior), an engineering assistant, pauses before its serverless deadline and queues a continuation. ([Sentry](https://cra.mr/building-an-intern/)) [Sierra's Agency](https://internal-agents.com/agents/sierra-pinecone) restores a sleeping runner by replaying events from its last checkpoint. ([Sierra](https://sierra.ai/es/blog/agency-secure-scalable-sandboxes-for-agents))

Each design keeps something different. A restored conversation doesn't mean the files survived, and replaying events doesn't undo what already happened in the outside world. When you read these accounts, check what each design says it brings back.

### Learn from failures, which are the least documented

Launch posts report what worked. The useful detail is usually in the retrospectives.

[Airbnb](https://internal-agents.com/agents/airbnb-airchat) built its own agent orchestrator and never shipped it. HubSpot found that starting a Kubernetes workload for every code review added latency, cost, and operational friction, so it rebuilt the reviewer. Dropbox moved its migrations to Nova because the previous tool couldn't recover interactively when a run failed. DoorDash published the two reviewer designs that came before the one that works.

Failures are probably common. Published failures are rare. Companies describe architecture freely, but rarely what an agent costs, how they evaluate it, or what they turned off. When a source doesn't say, the map records it as unknown.

## Read the numbers carefully, including the ones in the map

Almost every metric in the map is a company reporting on its own agent, and most of them only go up. Shopify called its own River adoption numbers "already wrong, in the upward direction." They can still be true. They're just easy to misread.

The best independent warning we found comes from METR. In a controlled study, experienced open-source developers using early-2025 AI tools took longer on their tasks while believing the tools had made them faster. ([METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)) METR's February 2026 update suggests newer tools are more likely to speed developers up, but says its data can't measure that reliably. ([METR](https://metr.org/blog/2026-02-24-uplift-update/)) The lesson that holds is about measurement: what people feel and what you measure can point in opposite directions.

So the map quotes every number exactly as published, with its date and scope. When a company's own article contradicts itself, we keep both versions and say so.

## Some of this depends on today's models

Anthropic wrote that "every component in a harness encodes an assumption about what the model can't do on its own." The same team removed parts of its own harness when newer models made them unnecessary. ([Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps))

We expect the scaffolding that makes up for model weaknesses to shrink. Permissions, audit records, and recovery protect the organization from any worker, human or model, so we expect those to stay.

## What we tell people now

When a team asks us where to start, this is roughly what we say:

- Start with work that a person can check quickly.
- Put the agent where the work already happens.
- Use code for anything that must always happen.
- Decide when the agent stops before you decide how clever it is.
- Keep the record of the work outside the worker.
- Test on your own past work, and keep the checker separate from the builder.

## What the map doesn't know yet

The map is strongest where companies publish the most, which is coding and code review. Support, finance, operations, and security are thinner, although Embat and Ramp show that interesting work happens there. The map also takes no position on building versus buying. It records what companies built or adapted.

## Use it, and help us fix it

On the [Internal Agents Map](https://internal-agents.com/) you can browse agents by the problem they solve, compare how different teams handled the same question, and read short [lessons](https://internal-agents.com/lessons) on stopping, review noise, splitting work, and more. Every claim links to its source, and every record exports as Markdown or JSON.

If you've built an internal agent, or read about one we missed, [suggest it on GitHub](https://github.com/steel-experiments/internal-agents-map/issues/new?template=catalog-suggestion.yml). We especially want the failures.
