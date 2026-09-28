// ABOUTME: Holds the text of the two guides: headings, paragraphs, list items, and links.
// ABOUTME: The HTML pages and their Markdown exports render the same values from here.

import { termLabel } from './labels';
import { SITE_NAME } from './metadata';
import { canonicalUrl, entryPath, guidePath, lessonsIndexPath } from './routes';

export const DEFINITIONS_TITLE = `What makes an agent internal? · ${SITE_NAME}`;
export const DEFINITIONS_HEADING = 'What makes an agent internal?';
export const DEFINITIONS_DESCRIPTION =
  'How organizations turn general-purpose models into agents for their own work. ' +
  'Explore workflow breadth, organizational adaptation, and practical agent terminology.';

export const METHODOLOGY_TITLE = `Methodology · ${SITE_NAME}`;
export const METHODOLOGY_HEADING = 'Methodology';
export const METHODOLOGY_DESCRIPTION =
  'How Internal Agents Map records sources, separates reported claims from interpretation, ' +
  'and handles uncertainty.';

export const LESSONS_TITLE = `Lessons · ${SITE_NAME}`;
export const LESSONS_HEADING = 'Lessons';
export const LESSONS_DESCRIPTION =
  'Short lessons on agent design. Each lesson connects an observation to reports from teams ' +
  'that build internal agents.';
export const LESSONS_LEDE = 'Short observations for people who build agents.';
/** The two halves of the introduction, around the link to the catalog. */
export const LESSONS_INTRO_BEFORE = 'Each lesson examines a design choice from the ';
export const LESSONS_INTRO_AFTER =
  '. Sources describe what teams report. Our observations explain what those reports may ' +
  'mean for other builders.';
export const LESSONS_CLOSING =
  'These lessons describe selected cases. They do not establish that one design works best ' +
  'for every team.';

export interface GuideLink {
  readonly label: string;
  readonly url: string;
}

/** The repository documents the Methodology guide sends a reader to. */
export const REPOSITORY_LINKS: readonly GuideLink[] = [
  {
    label: 'Data schema',
    url: 'https://github.com/steel-experiments/internal-agents-map/blob/main/data/schema.md',
  },
  {
    label: 'Lesson writing rules',
    url: 'https://github.com/steel-experiments/internal-agents-map/blob/main/docs/lessons-writing.md',
  },
  {
    label: 'Contribution guide',
    url: 'https://github.com/steel-experiments/internal-agents-map/blob/main/CONTRIBUTING.md',
  },
];

export interface ReferencePlacement {
  readonly id: string;
  /** The position on the Definitions chart, from 0 to 100 on each axis. */
  readonly x: number;
  readonly y: number;
  readonly name: string;
  readonly category: string;
  readonly reason: string;
  readonly links: readonly GuideLink[];
}

/**
 * Products and categories shown for comparison on the Definitions chart.
 * They are not catalog entries: they describe a default, unadapted setup.
 */
export const REFERENCE_PLACEMENTS: readonly ReferencePlacement[] = [
  {
    id: 'deep-research',
    x: 5,
    y: 19,
    name: 'Deep research agent',
    category: 'Research workflow',
    reason:
      'A ready-made agent for one research workflow: finding sources, reasoning across them, ' +
      'and producing a documented report. OpenAI, Google, and Perplexity offer examples.',
    links: [
      { label: 'OpenAI deep research', url: 'https://openai.com/index/introducing-deep-research/' },
      {
        label: 'Gemini Deep Research',
        url: 'https://support.google.com/gemini/answer/15719111?hl=en',
      },
      {
        label: 'Perplexity Research',
        url: 'https://www.perplexity.ai/help-center/en/articles/10738684-what-is-research-mode',
      },
    ],
  },
  {
    id: 'ready-made-task',
    x: 17,
    y: 29,
    name: 'Codex / Claude Code / Copilot',
    category: 'Software engineering agents',
    reason:
      'Ready-made agents that cover several software engineering workflows. Repository ' +
      'instructions, internal development tools, and company processes can move a deployment upward.',
    links: [
      { label: 'Codex overview', url: 'https://developers.openai.com/' },
      {
        label: 'Claude Code overview',
        url: 'https://docs.anthropic.com/en/docs/claude-code/getting-started',
      },
      { label: 'GitHub Copilot overview', url: 'https://github.com/features/copilot' },
    ],
  },
  {
    id: 'general-assistant',
    x: 76,
    y: 36,
    name: 'ChatGPT / Claude',
    category: 'Default setup · reference products',
    reason:
      'General-purpose assistants that span many kinds of work. Company knowledge, connected ' +
      'apps, and custom tools can move a deployment upward.',
    links: [
      { label: 'ChatGPT use cases', url: 'https://learn.chatgpt.com/use-cases' },
      {
        label: 'Claude enterprise search',
        url: 'https://support.claude.com/en/articles/12489464-use-enterprise-search',
      },
    ],
  },
];

/** One piece of a text block: plain words, bold words, or a link. */
export type Inline = string | InlineStrong | InlineLink;

export interface InlineStrong {
  readonly strong: string;
}

export interface InlineLink {
  readonly text: string;
  /** An address outside the website. */
  readonly href?: string;
  /** A path inside the website. The Markdown export makes it absolute. */
  readonly path?: string;
}

/** One text block, such as a paragraph or a caption. */
export type TextBlock = readonly Inline[];

/** A link from a guide header to a section of the same page. */
export interface JumpLink {
  readonly label: string;
  readonly fragment: string;
}

/** The address a link part uses inside a page. */
export function inlineHref(link: InlineLink): string {
  return link.href ?? link.path ?? '';
}

/** The Markdown form of one text block. */
export function inlineMarkdown(parts: TextBlock): string {
  return parts
    .map((part) => {
      if (typeof part === 'string') return part;
      if ('strong' in part) return `**${part.strong}**`;
      return `[${part.text}](${part.href ?? canonicalUrl(part.path ?? '')})`;
    })
    .join('');
}

/** The plain words of one text block, without bold marks or addresses. */
export function inlineText(parts: TextBlock): string {
  return parts
    .map((part) => (typeof part === 'string' ? part : 'strong' in part ? part.strong : part.text))
    .join('');
}

/** One part of the Methodology guide. */
export interface GuideSection {
  readonly id: string;
  /** The identifier of the heading, which labels the section. */
  readonly titleId: string;
  readonly heading: string;
  readonly body: readonly TextBlock[];
  readonly table?: {
    readonly headings: readonly string[];
    readonly rows: readonly (readonly string[])[];
  };
  /** The documents the section sends a reader to. */
  readonly links?: readonly GuideLink[];
}

export const METHODOLOGY_LEDE =
  'The map collects public accounts of internal agents and their infrastructure. It reflects what organizations choose to publish, so it cannot tell us how common a practice is across the industry.';

const CONTRIBUTING_URL =
  'https://github.com/steel-experiments/internal-agents-map/blob/main/CONTRIBUTING.md';

export const METHODOLOGY_SECTIONS: readonly GuideSection[] = [
  {
    id: 'methodology',
    titleId: 'inclusion-title',
    heading: 'What we include',
    body: [
      [
        'Each case identifies an organization, the internal work its system serves, and what the team built or materially adapted. Public evidence must describe the implementation or its use.',
      ],
      [
        'Adaptation can mean connecting internal tools, supplying company context, or adding workflow logic or controls. Buying licenses or announcing adoption alone does not qualify. Systems can qualify without a product name or a minimum amount of custom code.',
      ],
      [
        'Agents perform identifiable work. The Infrastructure collection covers implemented platforms and components that support agent workflows. Prototypes and research implementations can qualify; each entry states its deployment stage. Commercial and open-source systems follow the same evidence requirements.',
      ],
    ],
  },
  {
    id: 'intake',
    titleId: 'intake-title',
    heading: 'How we review cases',
    body: [
      [
        'We read the sources, check for an existing record, and assess the case against our ',
        { text: 'inclusion rules', href: `${CONTRIBUTING_URL}#inclusion-rules` },
        '. We add a case, update its existing entry, record what evidence is missing, or explain why it is out of scope. New evidence can reopen a decision.',
      ],
      [
        'Agents help prepare changes and check claims against source passages. Maintainers publish accepted changes by merging pull requests. Automated checks catch structural errors, damaged source files, and broken links. They cannot confirm an interpretation or reported result. Agreement between reviewing agents is not independent evidence.',
      ],
    ],
  },
  {
    id: 'sources',
    titleId: 'sources-title',
    heading: 'How we use sources',
    body: [
      [
        'We prefer original accounts. Attributed outside reporting can also support a case. We record each publisher’s relationship to the work and link claims to sources that support, contradict, or provide context for them. Passage locators identify the evidence where available. An article repeating a company’s result is not independent verification.',
      ],
      [
        'We preserve source pages with ',
        {
          text: 'Steel',
          href: 'https://steel.dev/',
        },
        '. Citations retain the publisher’s URL and link to the saved copy when one is available. Entries that cite the same source version at the same URL can share a capture. Its date tells you when we saved that copy. Preservation does not verify the claims it contains.',
      ],
      [
        'We distinguish reported facts, attributed opinions, and our own inferences. Company results remain self-reported unless separately verified. For metrics, we retain the reported scope, dates, denominator, and measurement method when available. Conflicting reports stay visible with their qualifications.',
      ],
    ],
  },
  {
    id: 'confidence',
    titleId: 'confidence-title',
    heading: 'What confidence means',
    body: [
      [
        'We assess confidence for each claim, with a reason that identifies its evidence and any unresolved step. Publisher identity alone never supplies a rating. Evidence strength describes source type and detail.',
      ],
      [
        'A source can clearly support “the company reports a reduction” without independently verifying the reduction. Read the attribution and qualifications alongside the rating.',
      ],
    ],
    table: {
      headings: ['Confidence', 'Meaning'],
      rows: [
        ['High', 'Direct, specific evidence supports the claim as worded and scoped.'],
        ['Medium', 'The evidence supports the main point, with a qualification or inference explained in the reason.'],
        ['Low', 'Support is weak, ambiguous, or conflicting.'],
        ['Unverified', 'Review has not established enough support for the claim.'],
        ['Not assessed', 'No explicit confidence rating is recorded. The source may still have been reviewed.'],
      ],
    },
  },
  {
    id: 'uncertainty',
    titleId: 'uncertainty-title',
    heading: 'When an answer is missing',
    body: [
      [
        'Unknown means the catalog has not established a classification. A capability or human supervision may still be present. Review states explain why a question has no answer.',
      ],
    ],
    table: {
      headings: ['Review state', 'Meaning'],
      rows: [
        ['Not reported', 'The reviewed sources do not establish the requested detail.'],
        ['Not reviewed', 'The assessment is unfinished. A note records the next research action.'],
        ['Not applicable', 'The question does not fit this system or workflow. A note explains why.'],
      ],
    },
  },
  {
    id: 'documentation',
    titleId: 'documentation-title',
    heading: 'What In depth means',
    body: [
      [
        'In depth identifies records with detailed primary evidence about their purpose and implementation. Every claim has a supporting source. All sources have preserved copies and have been reviewed, along with the reader questions and implementation fields. A shared capture counts for every entry that cites that source version.',
      ],
      [
        'A completed review can leave a question unanswered or mark it not applicable. Records can qualify with low-confidence claims or conflicting evidence. In depth describes documentation coverage. It does not certify performance or reported results.',
      ],
      [
        'By default, your bookmarks come first, then the entries we feature, followed by other In depth entries. Alphabetical sorting ignores these distinctions.',
      ],
    ],
  },
  {
    id: 'levels',
    titleId: 'levels-title',
    heading: 'How we assign levels',
    body: [
      [
        'For each named workflow, we assess whether and when human attention is required. The levels distinguish continuous participation, review of the work product, review of the outcome, and intervention only on exceptions. Each assessment cites evidence and a date.',
      ],
      [
        'One system can have different levels for different workflows. A single review boundary may not apply to shared infrastructure. Permissions to publish, merge, or act in production are recorded separately. The levels do not rank companies or output quality. See ',
        { text: 'the supervision definitions', path: `${guidePath('definitions')}#supervision` },
        ' for the terms and framework.',
      ],
    ],
  },
  {
    id: 'lessons',
    titleId: 'lessons-title',
    heading: 'How we write lessons',
    body: [
      [
        'We compare design choices across cases. Each ',
        { text: 'lesson', path: lessonsIndexPath() },
        ' links to its sources and separates what teams report from our observations.',
      ],
      [
        'We state the limits of each comparison. A repeated choice does not prove that it works better. Our illustrations explain the ideas and identify simplifications.',
      ],
    ],
  },
  {
    id: 'updates',
    titleId: 'updates-title',
    heading: 'Corrections and review dates',
    body: [
      [
        'We apply corrections and new evidence to the existing record. We keep conflicting accounts and label historical implementations so an older design is not attributed to its replacement. You can submit a source or correction through the contribution link below.',
      ],
      [
        'An entry’s review date records editorial work on the catalog. A source’s verification date records its last successful check at the original URL. Rereading a saved copy does not advance that date. Capture dates record when we saved the evidence. A metric’s observation date and measurement period come from the source.',
      ],
      [
        'Scheduled link checks test availability. They do not establish that a described system is still operating or that its reported results remain current.',
      ],
    ],
  },
  {
    id: 'limits',
    titleId: 'limits-title',
    heading: 'What the map cannot tell you',
    body: [
      [
        'Many documented cases concern coding and code review. Failed projects and unpublished systems may be missing, and companies decide which details and results to disclose.',
      ],
      [
        'Counts describe catalog records, including agent families, and do not measure independent deployments. Several entries can share infrastructure or cite the same account. Results from different tasks or measurement methods may not be comparable.',
      ],
    ],
    links: REPOSITORY_LINKS,
  },
  {
    id: 'logos',
    titleId: 'logos-title',
    heading: 'Company logos',
    body: [
      [
        'Logos identify organizations and remain their owners’ trademarks. They imply no endorsement, partnership, or quality judgment. If an owner requests removal, we replace the logo with a monogram and keep the entry.',
      ],
    ],
  },
];

/** A label above a value, such as a step of the workflow figure. */
export interface LabelledValue {
  readonly label: string;
  readonly value: string;
}

/** One end-to-end axis of the chart, from the first value to the last. */
export interface AxisScale {
  readonly from: string;
  readonly to: string;
}

/** One of the two questions the chart asks about an implementation. */
export interface ChartDimension {
  readonly heading: string;
  readonly description: TextBlock;
}

/** The heading of one region of the chart. */
export interface ChartCell {
  readonly scope: string;
  readonly title: string;
}

/** One picture of the terminology section, with its description. */
export interface ConceptFigure {
  /** The text a reader hears in place of the picture. */
  readonly label: string;
  readonly term: string;
  readonly caption: string;
}

/** One question and answer of the guide. */
export interface GuideQuestion {
  readonly question: string;
  readonly answer: TextBlock;
}

export interface ClassificationDefinition {
  readonly id: string;
  readonly label: string;
  readonly meaning: string;
}

export interface SupervisionDefinition extends ClassificationDefinition {
  readonly level: string;
  readonly attention: string;
}

const MINIONS_PATH = entryPath('stripe-minions');
const MINIONS_PART_ONE =
  'https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents';
const MINIONS_PART_TWO = `${MINIONS_PART_ONE}-part-2`;

export const DEFINITIONS_LEDE =
  'An agent is internal when it does a company’s own work with the company’s own context and tools.';

export const DEFINITIONS_INTRO: readonly TextBlock[] = [
  [
    'A model alone doesn’t know the codebase, follow the processes, or reach the tools. The organization supplies those, and shapes how the agent works.',
  ],
  [
    'This guide explains the terms the map uses. The map itself records what each system does, how the team built or adapted it, and what public evidence says about its use.',
  ],
];

export const DEFINITIONS_JUMP_LINKS: readonly JumpLink[] = [
  { label: 'Internal agents ↓', fragment: 'terms' },
  { label: 'How agents fit ↓', fragment: 'quadrant' },
  { label: 'Supervision ↓', fragment: 'supervision' },
  { label: 'Other terms ↓', fragment: 'terminology' },
];

export const WORK_DOMAIN_DESCRIPTION =
  'Work domain describes the kind of work an entry supports, such as coding, code review, support, or finance operations. One entry can cover several domains. This differs from workflow breadth, which describes how narrowly or broadly the system works.';

export const WORK_MODES_DESCRIPTION =
  'Work modes describe how work starts or proceeds. Interactive (foreground) and background describe participation; scheduled and event-driven describe triggers. One system can support several modes, such as event-driven background work.';

export const APPROACH_TYPE_DEFINITIONS: readonly ClassificationDefinition[] = [
  { id: 'agent', label: termLabel('agent'), meaning: 'One system that carries out tasks.' },
  { id: 'agent-system', label: termLabel('agent-system'), meaning: 'Several agents that each do useful work on their own and ship as one family.' },
  { id: 'platform', label: termLabel('platform'), meaning: 'Shared infrastructure that several agents or workflows run on.' },
  { id: 'orchestration-system', label: termLabel('orchestration-system'), meaning: 'A system whose primary role is coordinating agents.' },
  { id: 'supporting-pattern', label: termLabel('supporting-pattern'), meaning: 'One component, such as a sandbox or a context layer, that agents depend on.' },
];

export const INVOCATION_DEFINITIONS: readonly ClassificationDefinition[] = [
  { id: 'interactive', label: termLabel('interactive'), meaning: 'A person starts and exchanges messages with the system. This is foreground participation while those exchanges continue.' },
  { id: 'background', label: termLabel('background'), meaning: 'Work continues without continuous interaction after it starts.' },
  { id: 'scheduled', label: termLabel('scheduled'), meaning: 'A time rule starts the work.' },
  { id: 'event-driven', label: termLabel('event-driven'), meaning: 'A system event starts the work.' },
  { id: 'unknown', label: termLabel('unknown'), meaning: 'The collected evidence does not establish how work starts or proceeds.' },
];

export const SUPERVISION_DEFINITIONS = {
  heading: 'Supervision: when does a person look?',
  intro: [
    'A supervision level describes whether and when a person must take part in a named workflow. Some successful runs need no routine human review.',
  ] as TextBlock,
  source: [
    'The levels follow ',
    {
      text: "Dan Shapiro’s five levels of AI-assisted software development",
      href: 'https://www.danshapiro.com/blog/2026/01/the-five-levels-from-spicy-autocomplete-to-the-software-factory/',
    },
    '. Levels 0 and 1 cover manual work and autocomplete, so the catalog starts at level 2.',
  ] as TextBlock,
  rows: [
    { id: 'continuous-steering', label: termLabel('continuous-steering'), level: '2', attention: 'A person pairs with the agent throughout execution.', meaning: 'The person repeatedly guides the work as it proceeds.' },
    { id: 'work-product-review', label: termLabel('work-product-review'), level: '3', attention: 'A person reviews the draft or implementation.', meaning: 'The named workflow requires a person to inspect the work product. Publication permissions are recorded separately.' },
    { id: 'outcome-review', label: termLabel('outcome-review'), level: '4', attention: 'A person evaluates tests, behavior, or outcomes.', meaning: 'The normal review boundary is the result rather than routine implementation inspection.' },
    { id: 'exception-only', label: termLabel('exception-only'), level: '5', attention: 'A person returns when the system raises an exception.', meaning: 'A normal successful run does not require routine human review.' },
    { id: 'unknown', label: termLabel('unknown'), level: '—', attention: 'The catalog has not established a classification.', meaning: 'Review states distinguish missing evidence from unfinished assessment. A question that does not fit the system is not applicable; unknown does not mean no human supervision.' },
  ] as readonly SupervisionDefinition[],
  limits: [
    { strong: 'Attention is not authority.' },
    ' A background run can still lack permission to publish, merge, spend money, or act in production. A level also says nothing about how long the system runs unattended.',
  ] as TextBlock,
  scope: [
    'A level describes the named workflow and evidence date. It does not rank a company, maturity, autonomy, or output quality. One system can therefore have several scoped levels.',
  ] as TextBlock,
} as const;

/** Section 01: what the map calls an internal agent. */
export const DEFINITIONS_SCOPE = {
  eyebrow: '01 / The scope of the map',
  heading: 'What is an internal agent?',
  definitionLabel: 'Working definition',
  definition: [
    'An ',
    { strong: 'internal agent' },
    ' works with company context and tools to carry out the organization’s own work.',
  ] as TextBlock,
  diagramLabel: 'An agent connected to knowledge, tools, and workflows within an organization',
  body: [
    [
      'It might investigate a failed deployment, open a pull request, or help an employee resolve an IT issue. “Internal” describes the work it serves. The organization can build the system itself or adapt an existing product.',
    ],
    [
      'An agent answering customers directly serves a customer-facing role. One system can support both kinds of work.',
    ],
  ] as readonly TextBlock[],
  agentHeading: 'What makes it an agent?',
  agentBody: [
    [
      'For this guide, an ',
      { strong: 'agent' },
      ' uses a model to choose and carry out steps toward a task, using tools and feedback as it works.',
    ],
    [
      'Real systems often combine model-directed steps with programmed automation. A coding agent might decide how to fix a problem while a fixed pipeline runs tests and prepares the result for review.',
    ],
    ['The map separates task-performing Agents from the reusable Infrastructure that enables them. Lessons draw on both collections.'],
  ] as readonly TextBlock[],
} as const;

/** Section 02: one workflow, from the company task to the result. */
export const DEFINITIONS_WORKFLOW = {
  eyebrow: '02 / From a model to a workflow',
  heading: 'From a model to an internal workflow',
  intro: [
    'Consider ',
    { text: 'Stripe’s Minions', path: MINIONS_PATH },
    '. An engineer can ask a Minion to fix a flaky test. It works with Stripe’s code and development tools, makes a change, runs checks, and prepares a pull request for human review.',
  ] as TextBlock,
  steps: [
    { label: 'Company task', value: 'Fix a flaky test' },
    {
      label: 'Agent working with company context and tools',
      value: 'Stripe’s code · development environment · checks',
    },
    { label: 'Result in the company’s workflow', value: 'A pull request for human review' },
  ] as readonly LabelledValue[],
  caption: [
    'Sources: ',
    { text: 'Stripe’s workflow description', href: MINIONS_PART_ONE },
    ' and ',
    { text: 'execution environment', href: MINIONS_PART_TWO },
    '.',
  ] as TextBlock,
  closing: [
    'What makes this internal is its role in Stripe’s engineering work. Its cloud execution and unattended operation describe other aspects of the same system.',
  ] as TextBlock,
  catalogLink: {
    text: 'Explore Minions in the catalog',
    path: MINIONS_PATH,
  } as InlineLink,
} as const;

/** Section 03: the chart of work breadth and organizational adaptation. */
export const DEFINITIONS_CHART = {
  eyebrow: '03 / Different approaches',
  heading: 'How agents fit the organization',
  intro: ['Two questions separate the approaches in the map.'] as TextBlock,
  dimensions: [
    {
      heading: 'How broad is the work? (horizontal axis)',
      description: [
        'Focused agents follow one defined workflow. Broader agents perform many kinds of work. Shared platforms have a separate infrastructure index.',
      ],
    },
    {
      heading: 'How company-specific is it? (vertical axis)',
      description: [
        'Standard products arrive with common capabilities. Internal systems add company knowledge, tools, conventions, and processes.',
      ],
    },
  ] as readonly ChartDimension[],
  legend: { catalog: 'Catalog entry', reference: 'Reference product, default setup' },
  verticalAxis: { from: 'Standard capabilities', to: 'Company-specific capabilities' },
  horizontalAxis: { from: 'One workflow', to: 'Many workflows' },
  cells: {
    specialized: { scope: 'Company-specific · focused', title: 'Specialized internal agents' },
    shared: {
      scope: 'Company-specific · broad',
      title: 'General internal agents',
    },
    ready: { scope: 'Standard · focused', title: 'Ready-made focused agents' },
    assistants: { scope: 'Standard · broad', title: 'General-purpose assistants' },
  } as Record<string, ChartCell>,
  emptyCell: 'No selected example currently fits.',
  caption: [
    'Illustrative placements from public descriptions, not measured scores. An arrow runs from a standard product to a company system built on it.',
  ] as TextBlock,
  body: [
    [
      'The markers represent named systems and their documented scope. A company may operate several systems in different regions.',
    ],
    [
      'Broader scope and greater adaptation are not measures of quality. A focused agent may be exactly what a workflow needs.',
    ],
  ] as readonly TextBlock[],
  notesSummary: 'Why these systems are placed here',
  notesIntro: 'Spacing within a region is for readability.',
  builtHeading: 'What the team built or adapted',
  builtBody: [
    [
      'An organization can adapt an existing product deeply, or build a small custom agent for a narrow task. Building software in-house does not by itself tell us how broadly the system works or how closely it fits the organization.',
    ],
    [
      'Each catalog entry looks at the concrete choices: context, tools, execution environment, workflow, and the parts the team built or configured.',
    ],
  ] as readonly TextBlock[],
} as const;

/** Section 04: the other words a reader meets, and what each one answers. */
export const DEFINITIONS_TERMS = {
  eyebrow: '04 / Other terms',
  heading: 'Four more questions about the same system',
  intro: ['Each term answers a different question. They apply together.'] as TextBlock,
  place: {
    heading: 'Cloud and local: where does the work run?',
    definition: ['Local and cloud describe ', { strong: 'where the agent runs.' }] as TextBlock,
    figures: [
      {
        label: 'Local execution: the agent runs inside your device',
        term: 'Local',
        caption: 'Execution on your device',
      },
      {
        label: 'Cloud execution: your device connects to an agent running on a remote computer',
        term: 'Cloud',
        caption: 'Execution on hosted infrastructure',
      },
    ] as readonly ConceptFigure[],
    body: [
      [
        'A ',
        { strong: 'cloud agent' },
        ' executes on hosted infrastructure, independently of the user’s device.',
      ],
      [
        'A ',
        { strong: 'local agent' },
        ' executes on the user’s device. It may still call a model hosted in the cloud: model hosting and agent execution can happen in different places.',
      ],
      [
        'Stripe’s Minions run on AWS EC2 development machines, making them an example of cloud execution.',
      ],
    ] as readonly TextBlock[],
  },
  participation: {
    heading: 'Foreground and background: how do people interact with it?',
    definition: [
      'Foreground and background describe ',
      { strong: 'how you participate while it works.' },
    ] as TextBlock,
    figures: [
      {
        label: 'Foreground work: you send a message, the agent works, and its reply returns to you before the next exchange',
        term: 'Foreground',
        caption: 'Discuss, steer, and iterate as it works',
      },
      {
        label:
          'Background work: you hand off a task, the agent continues while your row is dotted, and the result returns to your row',
        term: 'Background',
        caption: 'Work proceeds without continuous interaction',
      },
    ] as readonly ConceptFigure[],
    body: [
      [
        { strong: 'Foreground work' },
        ' involves active interaction with a person: discussing the task, giving instructions, or steering the next steps.',
      ],
      [
        { strong: 'Background work' },
        ' proceeds without continuous interaction. A person can start it and return later, or a schedule or event can trigger it.',
      ],
      [
        'These are modes of work. The same agent can move between them. An engineer might give a Minion instructions, leave it to work, then return to discuss the result.',
      ],
    ] as readonly TextBlock[],
    switchingFigure: {
      term: 'One agent, changing modes',
      label: 'One task moves from foreground discussion to background work and back to foreground discussion. The same agent stays active. You participate at the beginning and end, and can step away while it continues on the Background work rail.',
      caption: 'Discuss the task, let the agent continue, then return to discuss the result.',
    } satisfies ConceptFigure,
  },
  combination: {
    label: 'These descriptions work together',
    lede: [
      'One agent can be ',
      { strong: 'internal, cloud-hosted, and background.' },
    ] as TextBlock,
    pairs: [
      { label: 'Whose work?', value: 'Internal' },
      { label: 'Where does it run?', value: 'Cloud' },
      { label: 'How do you participate?', value: 'Background' },
    ] as readonly LabelledValue[],
    note: 'A local agent can also work in the background. A cloud agent can work with you in the foreground.',
  },
  autonomy: {
    id: 'autonomy',
    heading: 'Autonomy: what can it do without approval?',
    body: [
      [
        { strong: 'Autonomy' },
        ' describes the decisions and actions an agent can take without human approval.',
      ],
    ] as readonly TextBlock[],
    lead: ['Describe that authority concretely:'] as TextBlock,
    quote:
      'A Minion can write code and run checks on its own. Production pull requests require human review.',
    closing: [
      'Working without someone’s continuous attention does not imply permission to take every action.',
    ] as TextBlock,
    recorded: [
      'The catalog records the authority a source describes. When an article explains a workflow but not its permissions, the entry says so instead of guessing.',
    ] as TextBlock,
  },
} as const;

/** Section 05: the questions readers ask about the definitions. */
export const DEFINITIONS_QUESTIONS = {
  eyebrow: '05 / Common questions',
  heading: 'Common questions',
  items: [
    {
      question: 'Does “internal” mean built in-house?',
      answer: [
        'No. A company can configure an existing product around its own workflows. The relevant question is what work the system serves and how it uses company context and tools.',
      ],
    },
    {
      question: 'Does “internal” mean private or self-hosted?',
      answer: [
        'No. An internal agent can use hosted services. Each entry describes hosting, data handling, and access controls on their own terms.',
      ],
    },
    {
      question: 'Is a shared agent platform itself an agent?',
      answer: [
        'A platform can provide the context, tools, execution environments, and controls used by multiple agents. The Infrastructure collection preserves this architecture research without counting platforms as agents. The default Agents collection covers the systems that perform identifiable work.',
      ],
    },
    {
      question: 'Is every automated workflow an agent?',
      answer: [
        'For this guide, the distinction is whether a model chooses steps or actions as the task unfolds. A fixed sequence of programmed steps is automation; a system can combine both.',
      ],
    },
    {
      question: 'Why are some details unknown?',
      answer: [
        'Public descriptions vary in depth. An article may explain a workflow without documenting its permissions or execution environment. The map leaves those details unknown rather than inferring them from a product name.',
      ],
    },
    {
      question: 'Are these official definitions?',
      answer: [
        'These are working definitions for reading the map. Product terminology varies. A concrete description of the work, context, tools, and behavior tells you more than any label.',
      ],
    },
  ] as readonly GuideQuestion[],
} as const;
