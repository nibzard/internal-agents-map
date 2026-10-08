> Archived source snapshot  
> Source ID: `embat-mr-batt-source-1`  
> Original URL: <https://www.embat.io/tech/internal-ai-agent-platform>  
> Final URL: <https://www.embat.io/tech/internal-ai-agent-platform>  
> Title: How We Built an Internal AI Agent Platform at Embat  
> Captured at: `2026-10-08T15:18:23Z`

---

Here you can read:

## The right answer was always in another room

At Embat we spend our days thinking about our customers' money, and almost as much time thinking about the data that describes it: balances, payments, reconciliations, bank connections, ERP syncs, and a lot of logs.

For a long time that information lived in separate rooms. When someone in the Product Experience team got a customer asking why a payment hadn't gone out, answering it usually meant pinging an engineer, who opened a database, who read a log, who checked a bank provider's dashboard. Everyone got there eventually, but slowly, and the person who actually wanted the answer was the furthest from it.

So the goal we set was simple to say and less simple to build: **one place to ask, one conversation, with all of those tools behind it**, and without anyone needing to know which system or which AI model did the work.

## It began as a support tool, not a chatbot

We started by helping our Product Experience team resolve customer issues faster, so we built an agent with real access to the things engineers reach for: our databases, our logs, our bank providers, our own code.

Once the tooling existed, the whole company wanted in. People finally had access to data and answers that previously required disturbing other people to obtain.That pull is what turned an internal support tool into **Agent M. Batt**. Yes, we were very creative with the naming.

## Build the harness, or borrow one?

The first real decision was whether to build our own agent framework from scratch or stand on something that already existed and spend our energy on tooling instead. We chose to borrow, and built on the **Claude Managed Agents** platform.

A solid base architecture, a strong model, and the sandboxing and plumbing already solved meant we could put our time where our advantage actually is: **the tools, the data access, and getting answers back to people quickly**. We'd rather ship impact than reinvent an agent loop.

![Claude Managed Agents Harness Architecture](https://www.embat.io/wp-content/uploads/2026/07/01-claude-managed-agents-platform.svg)

Claude Managed Agents Harness Architecture

## One giant brain, or a team of specialists?

The second decision was harder. Do you build one generalist agent that knows everything about Embat, or one agent per job?

We started with the single big agent, and it didn't take long to see the problem. To make it genuinely good, an agent that understood both Payments and Accounting deeply needed an enormous system prompt and a pile of skills, and every team that owned a domain kept needing to change things that touched everyone else's. **It was one file nobody fully owned, and even simple prompt changes in one domain degraded performance in another.**

**So we split it up.** Now each agent maps to a module, a task, or a set of tools, sized to its own complexity. Our **Payments Investigator**, for example, is completely independent from the general Accounting and Analytics work, and each team owns its own agent's behaviour without stepping on anyone else.

## Adding a new agent is almost boring

Splitting things up only works if adding an agent is cheap, and for us it mostly is. An agent is described in one place: **a system prompt, the set of tools it's allowed to call, and the code repositories it's allowed to read**. This is configurable even by people that have never touched a line of code in their lives. The routing, the Slack plumbing, the memory, the tool execution — none of that changes.

We started with two agents. **We're now past ten,** and they cover a surprisingly wide slice of the day to day: figuring out why a banking product didn't connect properly, helping the sales team answer ERP connectivity questions, serving metrics straight from our Semantic Layer, and plenty more.

## Knowing which agent to wake up

More than ten agents created a new problem, and it was a human one. Nobody could remember which command triggered which agent, or which agent was even the right one for a given question.

So we put **a router in front of everything**. Before a message ever reaches a specialist, a lightweight step reads the conversation and picks the agent that best fits. And because we don't want it guessing when it isn't sure, **we kept a human in the loop**: if the router isn't confident, it asks the person to choose rather than picking wrong and pretending otherwise. We also gave it an honest place for the messages that aren't really support requests at all, so a greeting or a joke doesn't get force-fitted into a payments investigation.

![Agent Routing System](https://www.embat.io/wp-content/uploads/2026/07/02-agent-router-1.svg)

Agent Routing System

## One platform, several providers, on purpose

In the introduction I mentioned closing the gap between different AI providers. Here's the nuance: **the goal is that the team chats with one platform, not that one provider does everything behind it.**

We deliberately delegate certain tasks to other providers. Part of that is practical, some jobs are simply a better fit elsewhere, and part of it is that we want to keep learning. One of our tools, for instance, spins up a **Google ADK agent** to do its work, which lets us feel the strengths and the rough edges of another agent framework first-hand instead of guessing about them. Staying multi-provider keeps us honest and keeps our options open.

## Wherever the conversation happens

Today almost everyone talks to Mr. Batt from Slack. But we didn't want to bet the architecture on Slack being forever, so **the platform doesn't actually know or care where a message comes from**. The conversation layer is fully separate from the channel. In practice that means we can point Mr. Batt at more or less any conversation surface that exposes an API, and the agents underneath don't need to change at all.

![Conversation Layer Independence](https://www.embat.io/wp-content/uploads/2026/07/03-conversation-layer-decoupled.svg)

Conversation Layer Independence

## This is just the introduction

Everything above is the shape of the thing, not the details. In the rest of this series we'll go into each piece properly: how the tooling is built and executed, how the agents share knowledge and memory, how we keep humans in control of the risky actions, and the less glamorous work of making all of this reliable in production.

Part 2 is coming very soon. Keep an eye out.

Interested in working with, or on, Agent Mr. Batt? We're hiring. [Open roles](https://www.embat.io/work-with-us)
