You are helping me build a personal second brain for distributed computing topics.

When I say "save as note", generate a structured note using this template and save it to the appropriate directory listed in README.md. If no existing directory fits, create a new one and add it to the directory list in README.md. Never save notes to the vault root.

```
# <name> — if the name is an abbreviation or initialism, include the full name in parentheses (e.g. `# MVCC (Multi-Version Concurrency Control)`)

<what it is in one sentence>

## Why it matters

<the problem it solves>

## How it works

<core mechanism, no fluff>

## Key tradeoffs

<what you give up>
```

After saving a new note, scan all existing notes for concepts that relate to the new note and add traditional markdown backlinks in both directions — in the new note and in any existing notes that reference the same concept. Use relative paths with `%20` for spaces (e.g. `[Note Name](../Dir/Note%20Name.md)`). Also look for backlink opportunities whenever editing existing notes.

After adding backlinks, regenerate the knowledge graph by running `python3 generate_graph.py` from the vault root.
