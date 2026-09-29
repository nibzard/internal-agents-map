// ABOUTME: Builds a contribution prompt for one catalog record.
// ABOUTME: Repository instructions remain the source of truth for the update process.
import { assertPublishableId, canonicalUrl, entryPath, markdownPath } from './routes';

export interface UpdateRecord {
  id: string;
  title: string;
}

export function updatePrompt({ id, title }: UpdateRecord): string {
  assertPublishableId(id);
  const path = entryPath(id);
  return `Help me update the Internal Agents Map record for ${title}.

Repository: https://github.com/steel-experiments/internal-agents-map
Record: data/agents/${id}.yaml
Published record: ${canonicalUrl(path)}
Readable context: ${canonicalUrl(markdownPath(path))}

Use the correction or public source I provide in this conversation.
If I have not supplied either, ask what I want changed before editing.

Use an existing checkout of this repository, or clone it if needed.
Read the current record from the repository. Follow AGENTS.md,
CONTRIBUTING.md, and the relevant instructions in data/schema.md.

Verify that the evidence supports the requested change. Preserve
uncertainty and distinguish reported facts from catalog judgments.
Follow the repository process for capturing new sources. If evidence
is insufficient, explain the gap instead of inventing details.

Make a focused change on a branch. Regenerate derived files and run
the required checks. Do not edit generated content by hand.

Show me the change, supporting evidence, and check results, including
any checks you could not run. Ask whether to submit a pull request
unless I already requested one. Do not merge the pull request.
If you cannot edit the repository, prepare a source-backed issue draft.`;
}
