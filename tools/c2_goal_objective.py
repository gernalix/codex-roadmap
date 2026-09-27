"""Small, durable objective for a C2 Goal thread.

The canonical prompt remains the first-turn input. The thread goal is recovery
context, so it must not become a second copy of that prompt.
"""
from __future__ import annotations

import re


_CONTRACT_HEADING = re.compile(
    r"(?:goal|obiettivo|objective|outcome|scope|scopo|vincol|invariant|"
    r"acceptance|criteri|requisit|esclusion|non.goal|stop)", re.IGNORECASE
)
_HEADING = re.compile(r"^#{1,3}\s+(.+?)\s*$", re.MULTILINE)
_PLAIN_HEADING = re.compile(
    r"^(Hard constraints|Verified residual gaps|Acceptance|Scope|Invariants|Goal):\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def compact_goal_objective(*, prompt_id: str, title: str, prompt: str) -> str:
    """Keep the explicit contract sections and a canonical recovery pointer.

    The selected sections are copied without truncation: silently shortening a
    constraint would change the task. Progress belongs in the task checkpoint.
    """
    matches=list(_HEADING.finditer(prompt))
    sections=[]
    for index, match in enumerate(matches):
        if _CONTRACT_HEADING.search(match.group(1)):
            end=matches[index+1].start() if index+1<len(matches) else len(prompt)
            section=prompt[match.start():end].strip()
            if section:
                sections.append(section)
    if not sections:
        plain=list(_PLAIN_HEADING.finditer(prompt))
        if not plain:
            raise ValueError('goal_contract_sections_missing')
        intro=prompt[:plain[0].start()]
        intro='\n'.join(line for line in intro.splitlines()
            if not line.startswith(('PROMPT_ID=', 'C2_WORK_ITEM_ID='))).strip()
        if intro:
            sections.append(intro)
        for index, match in enumerate(plain):
            end=plain[index+1].start() if index+1<len(plain) else len(prompt)
            sections.append(prompt[match.start():end].strip())
    checkpoint=f'operations/task-state/{prompt_id}.md'
    return '\n'.join([
        f'C2 Goal PROMPT_ID={prompt_id}: {title.strip()}',
        'Canonical source: C2 work item prompt:'+prompt_id+' and its writer-owned state.',
        'On resumption, read the compact checkpoint '+checkpoint+' first, then query '
        'the current C2 state. Do not replay the pasted prompt or full chat history.',
        'Preserve every mandatory scope rule and invariant from the canonical '
        'prompt. The core contract excerpts follow. Maintain the checkpoint with '
        'verified progress, remaining work, and exactly one next action.',
        '', *sections,
    ])
