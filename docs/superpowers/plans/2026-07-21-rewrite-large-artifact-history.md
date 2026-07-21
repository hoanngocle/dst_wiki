# Large Artifact History Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove crawler captures and `wiki.sqlite` from every commit reachable from `master`, then safely replace the GitHub `master` history.

**Architecture:** Create an external Git bundle before changing commit identities. Rewrite only `master` with an index filter so active local worktree branches remain untouched, verify the rewritten graph locally, then push with an explicit force-with-lease bound to remote commit `231fc01a8f258b45a4fd2b1ac751d771d900a03d`.

**Tech Stack:** Git 2.x, Git LFS, GitHub SSH remote

## Global Constraints

- Preserve `/Users/nyx/company/dst_wiki/data/crawled/` and `/Users/nyx/company/dst_wiki/data/generated/wiki.sqlite` on disk.
- Preserve the untracked `docs/category-crawler-control.md` file.
- Rewrite only `master`; do not alter local branches checked out by linked worktrees.
- Never use an unconstrained force push.
- Do not claim that history rewriting removes Git LFS objects from GitHub billing storage.

---

### Task 1: Create a recoverable pre-rewrite snapshot

**Files:**
- Create outside repository: `/tmp/dst_wiki-pre-history-rewrite-bdc1a45.bundle`
- Create outside repository: `/tmp/dst_wiki-category-crawler-control-pre-history-rewrite.md`

**Interfaces:**
- Consumes: all current Git refs and the untracked crawler-control document
- Produces: a verified rollback bundle and an independent copy of the untracked document

- [ ] **Step 1: Copy the untracked document**

Run:

```bash
cp docs/category-crawler-control.md /tmp/dst_wiki-category-crawler-control-pre-history-rewrite.md
```

Expected: both files have identical SHA-256 checksums.

- [ ] **Step 2: Create and verify the Git bundle**

Run:

```bash
git bundle create /tmp/dst_wiki-pre-history-rewrite-bdc1a45.bundle --all
git bundle verify /tmp/dst_wiki-pre-history-rewrite-bdc1a45.bundle
```

Expected: bundle verification reports every recorded ref as complete.

### Task 2: Rewrite and validate local master

**Files:**
- Rewrite: Git commits reachable from `refs/heads/master`
- Preserve: every working-tree file ignored by `.gitignore`

**Interfaces:**
- Consumes: pre-rewrite `master` and verified backup bundle
- Produces: rewritten `master` with no `data/crawled/**` or `data/generated/wiki.sqlite` path in its reachable history

- [ ] **Step 1: Rewrite master with an index filter**

Run:

```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter 'git rm -r --cached --ignore-unmatch -q data/crawled data/generated/wiki.sqlite' --prune-empty -- master
```

Expected: Git rewrites `master` and creates `refs/original/refs/heads/master` as an additional local fallback.

- [ ] **Step 2: Verify rewritten history and preserved local data**

Run:

```bash
git rev-list master --objects -- data/crawled data/generated/wiki.sqlite
git lfs ls-files master
git fsck --full
npm test
npm run build
```

Expected: both history queries produce no artifact paths, `git fsck` reports no corruption, all 124 tests pass, and the production build exits successfully. The ignored local data and untracked document must still exist with their pre-rewrite sizes/checksum.

### Task 3: Replace remote master safely

**Files:**
- Update remote ref: `origin/master`

**Interfaces:**
- Consumes: verified rewritten `master`
- Produces: GitHub `master` whose reachable history contains no crawler or SQLite artifacts

- [ ] **Step 1: Force-push with an explicit lease**

Run:

```bash
git push --force-with-lease=master:231fc01a8f258b45a4fd2b1ac751d771d900a03d origin master:master
```

Expected: GitHub accepts the rewritten `master`; the command refuses automatically if remote `master` changed after the preflight fetch.

- [ ] **Step 2: Fetch and verify the remote ref**

Run:

```bash
git fetch origin --prune
git rev-list origin/master --objects -- data/crawled data/generated/wiki.sqlite
git lfs ls-files origin/master
```

Expected: remote history queries produce no artifact paths and `origin/master` equals local `master`.

- [ ] **Step 3: Remove the temporary original-master ref**

Run:

```bash
git update-ref -d refs/original/refs/heads/master
```

Expected: the pre-rewrite history remains recoverable from `/tmp/dst_wiki-pre-history-rewrite-bdc1a45.bundle`, but is no longer retained by the filter-branch backup ref.
