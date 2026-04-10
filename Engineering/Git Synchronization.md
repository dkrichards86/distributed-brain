# Git Synchronization

How Git moves commits between repositories — copying objects and updating references — and when operations are safe vs. destructive.

## Why it matters

Push failures, rebase warnings, and merge conflicts all make sense once you understand that Git repositories are independent [[Git Internals|object databases]] that occasionally synchronize. The rules governing what's safe to push, when rebase rewrites history, and why merge conflicts happen all follow directly from the underlying model.

## How it works

### Push and pull

**Push** does two things:
1. Copies objects (commits, trees, blobs) the remote doesn't have
2. Updates the remote branch reference to your latest commit

Git only allows the reference update if your commit is a **descendant** of the current remote commit (fast-forward). If the remote has commits your branch doesn't, the push is rejected — updating the reference would lose those commits.

**Pull** = `fetch` + `merge` (or `rebase`, depending on config). Fetch copies objects and updates tracking branch references. Merge or rebase reconciles the diverged local and remote histories.

### Fast-forward vs. non-fast-forward

**Fast-forward:** Your commit's ancestry includes the remote's current commit. The reference just moves forward along the same chain — no history is lost.

**Non-fast-forward (diverged):** You and the remote have both added commits since the last sync. Neither history is a subset of the other. Git rejects a plain push; you must reconcile first.

### Merge

Creates a new commit with two parents — one from each diverged branch. Preserves history exactly as it happened, including the divergence and convergence.

- Safe: never loses commits
- Visible: history shows when branches diverged and merged
- Best for: preserving true development history

### Rebase

Replays your commits one by one on top of the target branch, creating *new* commit objects. The original commits are abandoned.

Why new objects? Each commit contains its parent's hash. Changing the parent means the hash changes, which means a new commit object.

- Result: linear history that looks like your changes were made on top of the latest remote commits
- Dangerous if others have your original commits — their history will diverge from yours after the rebase
- Best for: clean feature branch history before merging, code review clarity

**Golden rule:** Never rebase commits that have been pushed and shared. Once others base work on your commits, rebasing orphans their work.

### Interactive rebase

Lets you reorder, squash, split, or edit commit messages during replay. Each operation creates new commit objects, even just a message change. Useful for cleaning up a feature branch's history before merging.

### Conflict resolution

Conflicts occur when the same lines in the same files were changed differently in both branches. Git marks conflicted files and pauses.

- In a merge: resolve once, create the merge commit
- In a rebase: resolve for *each* replayed commit that touches the conflicting code — potentially multiple times for the same file

### Remote tracking branches

Local copies of remote branch references (e.g., `origin/main`). Updated when you `git fetch`. `git status` reports "3 ahead, 2 behind" by comparing your local branch to the tracking branch.

## Key tradeoffs

- **Merge vs. rebase** — merge preserves true history but adds merge commits; rebase produces clean linear history but rewrites commits and can confuse collaborators
- **Force push** — bypasses fast-forward requirements; allows pushing rebased branches but overwrites remote history for anyone tracking it. Destructive on shared branches.
- **Squash vs. preserve commits** — squashing before merge produces a clean main branch history but loses granular development context; individual commits make bisect easier
