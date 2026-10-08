> Archived source snapshot  
> Source ID: `ramp-finance-agents-source-1`  
> Original URL: <https://ramplabs.substack.com/p/we-built-an-agent-to-prompt-our-internal>  
> Final URL: <https://ramplabs.substack.com/p/we-built-an-agent-to-prompt-our-internal>  
> Title: We built an agent to prompt our internal finance agent  
> Captured at: `2026-10-08T15:18:29Z`

---

*[Ramp Labs](https://labs.ramp.com/) is the home for AI experiments from [Ramp](https://ramp.com/). We share learnings on applying the latest models to real-world problems. We also share insights into how Ramp is leveraging AI internally to increase productivity. Follow us on X [@RampLabs](https://x.com/RampLabs) and subscribe below.*

---

<video controls="" src="blob:https://ramplabs.substack.com/9d2a53e0-43c2-4180-b528-70c3040e0c0e"></video>

We built an internal finance agent that could automate hours of tedious accounting work in spreadsheets. But every time someone wanted to use it, they’d spend 30-45 minutes crafting the perfect prompt, uploading the right files, and resolving errors.

**We asked: what if the agent could watch us work and write its own prompts?**

So we built a second agent called the Architect. This agent watches screen recordings of accountants doing their jobs, extracts the workflow, identifies what external data is needed, and generates detailed prompts, all without human intervention. It then hands off everything to our Doer agent to execute the task.

**The result: what used to be dreaded hours wasted on tedious tasks now takes a five-minute screen recording. This is second-order automation: automation that creates automation.**

In this post, we’ll break down how we built this two-agent system for finance use cases and share performance benchmarks.

---

## The problem with first-order automation

Most AI agents today have a prompt problem. Our internal finance agent could automate complex accounting workflows, but it required perfectly crafted prompts and the right context files. Here are some sample tasks:

- Monthly revenue reconciliation exercise by consolidating invoice and data warehouse data into Excel to prepare and upload a journal entry into ERP.
- Month-end booking of inter-company fund transfers from several tools into an Excel workbook to create and import a journal entry into ERP.

This creates a paradox where the agent saves time executing tasks but costs time in setup. Accountants had to become prompt engineers trying to describe their process and if they wanted to run the same process next month, they had to re-write the prompt manually.

We realized that the bottleneck wasn’t execution but instruction.

---

## Second-order automation with Architect & Doer agents

![](https://substackcdn.com/image/fetch/$s_!g6ZW!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa82143c3-741a-477a-bc95-41db7fb52527_1536x1024.png)

Instead of focusing on making the internal finance agent marginally better, we needed another agent to setup the task itself. Our solution was a two-agent system where one agent generates instructions for the other.

**The Architect agent** watches screen recordings of users completing tasks. Using a large-context multimodal model, it:

- Extracts the step-by-step workflow
- Identifies when users paste external data or reference other files
- Generates detailed, structured prompts for the Doer agent
- Compiles everything into a reusable “Process”

**The Doer agent** (our internal finance agent) executes these instructions using specialized tools to search, manipulate, and validate spreadsheet operations.

As a result, our two-agent system could take a human-recorded workflow and, after watching it once, create an entirely reusable workflow without additional input.

---

## Deep dive into the two-agent system

**The Architect agent** solves this blueprint problem. Its role is to watch a human work through a spreadsheet via screen recordings and break the process into clear, specific instructions for our Doer agent to use in the future. The Architect agent also notes when users paste in data from external sources, or understands if other context is required (e.g. the current month) before running the Doer agent.

All of the Architect agent’s outputs are compiled into a **Process**: a compiled set of steps, required files, and additional information that will eventually be passed along to the Doer agent for each run.

### Architect agent flow

![](https://substackcdn.com/image/fetch/$s_!uuG0!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa2f61a60-46dc-41b5-a7e3-712cae6c5f06_1496x1330.png)

- User uploads screen recording of their workflow
- **Gemini 2.5 Pro (1M token context window)** processes video to extract actions and context
- Agent identifies required files and temporal dependencies (e.g. current month data)
- Generates structured prompt with step-by-step instructions
- Compiles into a Process that can be reused

### Doer agent flow

This agent is simple and relies as much as possible on model intelligence to achieve tasks with minimal guide rails.

![](https://substackcdn.com/image/fetch/$s_!SlRi!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9e635e61-d016-44b5-a045-4b12f7019333_2036x858.png)

- Receives process with instructions and uploaded files
- **Claude Sonnet 4.5** uses specialized tools to navigate and manipulate spreadsheets
- Executes each instruction with validation checks
- Returns completed spreadsheet

---

## Performance results

### Architect agent

While we haven’t yet developed a formal benchmark for the architect agent, we can see its impact in terms of workflow creation from non-technical users. Accountants simply upload a screen recording and come back to a ready-to-use process. The time savings are significant when compared with manual prompting for every run.

### Doer agent

We tested against [SpreadsheetBench](https://spreadsheetbench.github.io/) on ~50 randomly selected tasks (3 test cases each):

- Soft-restriction tasks: **49.5% accuracy** (vs. OpenAI’s 45.5%)
- Hard-restriction tasks: **32.5% accuracy** (vs. GPT-4o’s 13.38%)

Tasks taking 1-2 hours now complete in under 10 minutes (a 6-12x speedup). In cases of partial completion, the agent still saves significant time before human intervention is needed.

The barrier to automation collapsed from weeks of engineering work to simply recording your screen.

---

## Learnings

1. **Second-order changes the scaling equation.** First-order: Adding workflows scales linearly with human prompt-writing capacity. Second-order: Adding workflows costs near-zero human time once the architect agent exists.
2. **Models have complementary strengths.** Gemini 2.5 Pro’s 1 million token context window with stellar multimodal support allows us to capture key details from input videos to generate a process, while Anthropic’s Claude Sonnet 4.5 shines when it’s time get work done by being swift, precise, and economic.
3. **Building production agents is still hard.** Despite powerful models, we spent weeks iterating on system prompts, tool designs, and error handling. There’s no shortcut for testing, debugging, and refinement. The engineering matters as much as the models.

---

Our combined agent doesn’t just do work, it designs how work gets done. This unlocks a new scaling paradigm: instead of engineers building automations one by one, anyone who can record their screen can generate reusable workflows. The architect-doer pattern transformed automation from an engineering bottleneck into a self-service capability. The next frontier isn’t faster agents, it’s agents that teach themselves what to do.

Want to get early access to future AI experiments? Subscribe below and follow us on [X @RampLabs](https://x.com/RampLabs). We’re also [hiring across roles](https://jobs.ashbyhq.com/ramp?utm_source=RampLabs) at Ramp.
