# Vercel Artifact Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep crawler databases and raw captures available locally while removing them from Git LFS and Vercel deployment inputs.

**Architecture:** The Next.js runtime continues consuming generated files under `public/`. Raw crawler state under `data/crawled/` and the audit database at `data/generated/wiki.sqlite` become local-only artifacts excluded by both Git and Vercel.

**Tech Stack:** Git, Git LFS, Vercel, Next.js 16.2.10

## Global Constraints

- Preserve all local crawler and SQLite files on disk.
- Do not modify the application's runtime data flow.
- Do not touch unrelated untracked or modified files.
- Keep generated runtime JSON and public assets tracked.

---

### Task 1: Exclude local-only data artifacts

**Files:**
- Modify: `.gitignore`
- Modify: `.gitattributes`
- Create: `.vercelignore`
- Modify index only: `data/crawled/**`, `data/generated/wiki.sqlite`

**Interfaces:**
- Consumes: generated runtime artifacts under `public/`
- Produces: a deployment source tree without raw crawls or the SQLite audit database

- [x] **Step 1: Add Git ignore rules**

Add repository-root rules for `/data/crawled/` and `/data/generated/wiki.sqlite` so local regeneration does not restage those artifacts.

- [x] **Step 2: Remove obsolete Git LFS attributes**

Delete the six LFS tracking entries for the crawler JSONL/SQLite files and generated Wiki database. Leave unrelated attributes unchanged.

- [x] **Step 3: Add Vercel exclusions**

Create `.vercelignore` with:

```gitignore
data/crawled/
data/generated/wiki.sqlite
```

- [x] **Step 4: Stop tracking artifacts without deleting local files**

Run:

```bash
git rm -r --cached --ignore-unmatch data/crawled data/generated/wiki.sqlite
```

Expected: Git stages deletions, while every file remains present in the working tree and becomes ignored.

- [x] **Step 5: Verify repository and deployment boundaries**

Run:

```bash
git check-ignore -v data/generated/wiki.sqlite data/crawled/dontstarve-items/pages.jsonl
git ls-files data/crawled data/generated/wiki.sqlite
npm run build
```

Expected: both large paths match ignore rules, no crawler/database files remain in the Git index, and the production build exits successfully. `git lfs ls-files` continues describing `HEAD` until this staged change is committed.
