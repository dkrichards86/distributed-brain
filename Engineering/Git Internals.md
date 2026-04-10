# Git Internals

Git's underlying storage model: a content-addressable object database with four object types and a thin layer of references on top.

## Why it matters

Most Git confusion — detached HEAD, rebase vs. merge behavior, why `reset` has three modes — dissolves once you understand the object model. Git isn't magic; it's a database with a few clever abstractions. Knowing how it works lets you reason about what any operation will do before you run it.

## How it works

### The four object types

Everything in Git is stored as one of four immutable object types, each identified by a SHA-1 hash of its contents:

| Object | What it stores |
|---|---|
| **Blob** | Raw file contents — no filename, no path, just bytes |
| **Tree** | A directory listing: names, permissions, and pointers to blobs and other trees |
| **Commit** | A pointer to a tree (project state), parent commit hashes, author, timestamp, message |
| **Tag** | A named pointer to another object, usually a commit |

### Content addressing

Git doesn't store files by name — it stores them by content hash. Two files with identical content get the same hash and are stored once. This gives Git automatic deduplication and corruption detection: changing one bit changes the hash, so Git immediately knows something is wrong.

### The index (staging area)

The index is a binary file that tracks what goes into the *next* commit. It's a draft of your next tree.

- `git add` creates a blob for the file's current content and updates the index to point to it
- `git commit` creates a tree from the index, then a commit pointing to that tree
- The working directory and the index are independent — changes after `git add` aren't staged until you `git add` again

This is why `git diff` (working dir vs. index) differs from `git diff --cached` (index vs. last commit).

### Branches are just files

A branch is a text file in `.git/refs/heads/` containing a single SHA-1 hash — the commit it points to. Creating a branch creates a 40-character text file. Switching branches updates your working directory and moves `HEAD`.

**HEAD** is a special reference that points to the current branch (or directly to a commit in detached HEAD state).

### Commit history is a linked list

Each commit points to its parent commit(s). Git history is traversed by following parent pointers backward from the current commit. Merge commits have two parents. The initial commit has none.

When you commit, Git:
1. Creates a tree from the index
2. Creates a commit pointing to that tree, with the current branch's tip as the parent
3. Updates the branch reference to the new commit hash

The old commit is untouched — it's still in the object database.

## Key tradeoffs

- **Immutability** — objects are never modified in place; "rewriting history" ([[Git Synchronization|rebase]], amend) creates new objects and updates references, leaving orphaned old objects until GC
- **Content addressing** — perfect deduplication and integrity, but you can never look up a file by name across the object database directly
- **Cheap branches** — branches are just pointers, so they're free to create and fast to switch; this encourages short-lived feature branches and experimentation
- **Detached HEAD** — powerful for exploring history, but commits made in detached HEAD state are orphaned when you switch back unless you create a branch
