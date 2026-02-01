---
name: summarizing-new-skills
description: "Analyzes agent behavior logs and mission requirements to synthesize new, semantically clear Agent Skills. Use this skill when a user says 'codify this pattern', 'create a skill from these logs', or when a repetitive, successful workflow is detected. It excels at turning raw procedural knowledge into reusable, modular packages."
license: Proprietary. LICENSE.txt has complete terms
compatibility: "Works across all Agent Skills compatible platforms (Claude Code, Cursor, etc.)"
---

# Summarizing New Skills

Transform execution logs into a standard-compliant SKILL.md that minimizes context usage through progressive disclosure (agentskills.io).

## Goal

Produce a valid SKILL.md that:
- Accurately triggers in the intended context (semantic routing).
- Focuses on one specific workflow (atomicity).
- Optimizes instruction-to-token ratio by offloading logic to scripts where appropriate.

---

## When to Use

Use this skill when the user says or implies:
- **Trigger phrases**: "codify this pattern", "create a skill from these logs", "turn this into a reusable skill", "document this workflow as a skill".
- **Context signals**: A repetitive, successful multi-step workflow is present in logs and should be standardized into a reusable package.

## When NOT to Use

**Do NOT create a skill for:**
- One-off tasks or ad-hoc requests.
- Simple instructions that do not involve complex logic, multiple steps, or specific domain expertise.

Creating skills for trivial cases leads to skill bloat and weakens semantic routing. When in doubt, prefer a single well-scoped skill over many narrow ones.

---

## Instructions

### 1. Pattern Extraction (Input Analysis)

When processing agent logs and the target task, identify:

| Component | What to extract |
|-----------|-----------------|
| **Success Mining** | The exact sequence of tools and reasoning steps that led to the goal. |
| **Context Gap Identification** | What reference files (e.g., schemas, API docs) the agent had to read or search for to succeed. |
| **Variable Abstraction** | Hardcoded values (file paths, URLs, env names) that should become placeholders or script parameters. |
| **Hidden Requirements** | Implicit dependencies: e.g., if the agent repeatedly consulted a specific API doc or config file, that path should be extracted into the new skill's `references/` so the generated skill points to it explicitly. |
| **Decision Logic** | Heuristics used to choose one path over another. |
| **Failure Modes** | Steps that frequently led to errors and need strict constraints or scripts. |

### 2. Output Architecture

**Metadata (YAML Frontmatter):**
- **Name**: Gerund form, kebab-case (e.g., `optimizing-sql-queries`). Alphanumeric and hyphens only; no Unicode. Avoid vague names like `helper` or `utils`. Max 64 characters.
- **Description**: Third person only. State WHAT the skill does and WHEN to use it (trigger conditions). Include trigger phrases for semantic routing. Max 1024 characters.
- **compatibility** (optional): Environment or platform requirements, e.g. `"Requires Python 3.10+ for scripts"` or `"Works across all Agent Skills compatible platforms (Claude Code, Cursor, etc.)"`.

**Body structure:**
- If instructions exceed 500 lines, move detailed reference material to `references/`.
- **Degrees of Freedom**:
  - **High Freedom** (heuristics): Creative or complex reasoning.
  - **Medium Freedom** (templates/pseudocode): Standard patterns.
  - **Low Freedom** (specific scripts): Fragile, security-critical, or deterministic operations.
- **Terminology**: Use consistent terms throughout (e.g., "API endpoint" vs "URL").

### 3. Progressive Disclosure

| Level | Content |
|-------|---------|
| **Level 1 (Discovery)** | Frontmatter (name, description, optional compatibility). |
| **Level 2 (Activation)** | Core instructions and SOPs in the Markdown body. |
| **Level 3 (Execution)** | Scripts in `scripts/`, documentation in `references/`. |

### 4. Output Format Template

The output must be a valid SKILL.md with this structure:

```markdown
---
name: [gerund-kebab-case-name]
description: "[Third-person: what the skill does. When to use it, including trigger phrases.]"
compatibility: "[Optional. e.g. Requires Python 3.10+ for scripts]"
---

# [Skill Title]

## Goal
[Clear statement of what the skill achieves]

## Instructions
[Core steps, constraints, and rules]

## Examples
[Concrete few-shot input/output pairs]

## Guidelines
[Consistency and quality requirements]
```

---

## Constraints

- **Atomic Focus**: Each generated skill must handle exactly ONE cohesive workflow.
- **Third Person**: Use only third-person perspective in descriptions and instructions (e.g., "The agent should...", not "I will...").
- **No Unicode in name**: Use only alphanumeric characters and hyphens for the `name` field.

---

## Examples

### Example: From log to skill

**Input (log pattern):**  
Agent repeatedly runs `grep` to find error patterns in test output, then `sed` to fix the offending lines, then `npm test` to verify. This sequence succeeds across multiple runs.

**Generated skill name:**  
`fixing-test-regressions`

**Generated description:**  
"Automates the identification and repair of test regressions using grep and sed. Use when 'npm test' fails and logs show recurring patterns of known errors."

**Why it qualifies:** Multi-step workflow, repeatable pattern, clear success criteria, and benefit from being reused as a skill rather than re-explained each time.

---

## Guidelines

- **Semantic Test**: The description must accurately trigger the skill in the intended context (trigger phrases + scenario words).
- **Atomicity Test**: The skill must focus on one specific workflow.
- **Efficiency Test**: Optimize instruction-to-token ratio by offloading logic to scripts and `references/` where possible.

---

## Evaluation Criteria

A "Great" skill generated by this process must pass:

1. **Semantic Test**: Does the description include trigger phrases and accurately trigger in the intended context?
2. **Atomicity Test**: Does the skill focus on exactly one cohesive workflow?
3. **Efficiency Test**: Is the instruction-to-token ratio optimized (e.g., heavy detail in `references/` or scripts)?
4. **Negative Filter**: Was it correct *not* to create a skill (e.g., for one-off or trivial tasks)?
