#!/usr/bin/env python3
"""
Profile auto-updater — triggered manually via workflow_dispatch.

Pipeline:
  1. GitHub API  → fetch all public repos (stars, metadata, recent commits)
  2. AI (Gemini primary, Claude fallback) → analyse commits per repo, decide
     what changed, generate updated project descriptions / new repo entries
  3. Patch       → README.md  (star counts, new repos, descriptions, timestamp)
                   infographic.html  (project card descriptions, stat numbers)
                   scripts/resume_data.json  (project bullets)
  4. Build       → regenerate dated resume PDF via build_pdf.py

Secrets (set in repo Settings → Secrets → Actions):
  GITHUB_TOKEN      — auto-provided by Actions (needs contents: write)
  GEMINI_API_KEY    — primary AI provider (Google Gemini 2.5 Flash)
  ANTHROPIC_API_KEY — fallback AI provider (Claude Haiku) if Gemini unavailable

Run locally:
  export GITHUB_TOKEN=ghp_...
  export GEMINI_API_KEY=AIza...        # primary
  export ANTHROPIC_API_KEY=sk-ant-...  # fallback (optional)
  cd <repo-root>
  python scripts/update_all.py
"""

import os, re, sys, json, base64, textwrap, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).resolve().parent.parent
README        = ROOT / "README.md"
INFOGRAPHIC   = ROOT / "interactive-resume-infographic" / "infographic.html"
RESUME_DATA   = ROOT / "scripts" / "resume_data.json"
BUILD_PDF     = ROOT / "scripts" / "build_pdf.py"

# ─── Config ───────────────────────────────────────────────────────────────────
USERNAME       = "ChaitanyaEswarRajeshJakki"
GEMINI_MODEL   = "gemini-2.5-flash"
CLAUDE_MODEL   = "claude-haiku-4-5-20251001"
COMMIT_DAYS    = 14          # how far back to look for commits
SKIP_REPOS     = {"Chaitanya", "opencv", "GFPGAN"}
# Skip repos whose names contain a date (e.g. AppNova_Working_09-04-2026)
_DATE_IN_NAME  = re.compile(r'\d{2}-\d{2}-\d{4}')

GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN", "")
GEMINI_KEY     = os.environ.get("GEMINI_API_KEY", "")
ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")

GH_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

changes_log = []   # collected across all steps, printed at end

# ─── Utilities ────────────────────────────────────────────────────────────────
def log(msg):
    print(msg)
    changes_log.append(msg)

def gh(path, params=None):
    r = requests.get(f"https://api.github.com{path}",
                     headers=GH_HEADERS, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def _gemini(prompt):
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text.strip()
    except Exception as e:
        log(f"  [Gemini error] {e}")
        return None

def _claude(prompt):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        log(f"  [Claude error] {e}")
        return None

def ai_call(prompt):
    """Try Gemini first; fall back to Claude if unavailable."""
    if GEMINI_KEY:
        result = _gemini(prompt)
        if result:
            return result
    if ANTHROPIC_KEY:
        log("  [AI] Gemini unavailable, trying Claude fallback…")
        return _claude(prompt)
    return None

# ─── 1. GitHub data fetch ─────────────────────────────────────────────────────
def fetch_repos():
    repos, page = [], 1
    while True:
        batch = gh("/user/repos",
                   {"per_page": 100, "page": page, "type": "owner"})
        if not batch:
            break
        repos.extend(r for r in batch if not r["fork"])
        if len(batch) < 100:
            break
        page += 1
    return repos

def fetch_recent_commits(repo_name, since_days=COMMIT_DAYS):
    since = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
    try:
        commits = gh(f"/repos/{USERNAME}/{repo_name}/commits",
                     {"per_page": 20, "since": since})
        return [
            {
                "sha":     c["sha"][:7],
                "message": c["commit"]["message"].splitlines()[0],
                "date":    c["commit"]["author"]["date"][:10],
                "files":   [],   # filled lazily only if Gemini is available
            }
            for c in commits
        ]
    except Exception:
        return []

def fetch_commit_files(repo_name, sha):
    try:
        data = gh(f"/repos/{USERNAME}/{repo_name}/commits/{sha}")
        return [f["filename"] for f in data.get("files", [])]
    except Exception:
        return []

def fetch_repo_readme(repo_name):
    try:
        data = gh(f"/repos/{USERNAME}/{repo_name}/readme")
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")[:2000]
    except Exception:
        return ""

# ─── 2. AI analysis ──────────────────────────────────────────────────────────
def analyse_commits_for_project(repo_name, commits, current_description):
    """Return (updated_description, changed: bool) or (None, False) if no AI key set."""
    if not (GEMINI_KEY or ANTHROPIC_KEY) or not commits:
        return None, False

    commit_text = "\n".join(
        f"  [{c['date']}] {c['message']}" for c in commits
    )
    prompt = textwrap.dedent(f"""
        You are maintaining a GitHub profile README for a developer called Chaitanya.
        Below is the current one-sentence description for the project "{repo_name}" and the
        recent commit history. If the commits reveal meaningful new features, new tech, or
        significantly improved functionality that is NOT already reflected in the description,
        return a single updated sentence (max 25 words). Otherwise return the word UNCHANGED.

        Current description:
        {current_description}

        Recent commits (last {COMMIT_DAYS} days):
        {commit_text}

        Rules:
        - Return ONLY the updated sentence or the word UNCHANGED.
        - Keep the same tone (technical, third-person, concise).
        - Do NOT add quotes or explanation.
    """).strip()

    result = ai_call(prompt)
    if result and result.upper() != "UNCHANGED" and result != current_description:
        return result, True
    return current_description, False


def generate_new_repo_entry(repo):
    """Use AI to create README table row + overview line for a brand-new repo."""
    name   = repo["name"]
    desc   = repo["description"] or ""
    readme = fetch_repo_readme(name)

    prompt = textwrap.dedent(f"""
        You are updating a GitHub profile README for Chaitanya.
        A new public repository just appeared. Produce EXACTLY two lines, nothing else:

        LINE 1 — Markdown table row (keep | separators):
        | <emoji> **{name}** | <one sentence: what it does> | <Stack1 · Stack2 · Stack3> | [{name}](https://github.com/{USERNAME}/{name}) |

        LINE 2 — Overview bullet:
        - **[{name}](https://github.com/{USERNAME}/{name})** — <short description ≤12 words>

        Repo name: {name}
        GitHub description: {desc}
        README excerpt (first 1500 chars):
        {readme[:1500]}
    """).strip()

    result = ai_call(prompt)
    if not result:
        return None, None
    lines       = [l.strip() for l in result.splitlines() if l.strip()]
    table_row   = next((l for l in lines if l.startswith("|")), None)
    overview    = next((l for l in lines if l.startswith("-")), None)
    return table_row, overview


def generate_new_project_bullets(repo_name, commits, readme_text):
    """Generate resume bullet points for a brand-new project."""
    if not (GEMINI_KEY or ANTHROPIC_KEY):
        return []
    commit_text = "\n".join(f"  [{c['date']}] {c['message']}" for c in commits[:10])
    prompt = textwrap.dedent(f"""
        Write 2–3 concise resume bullet points (each ≤30 words, past tense, action verbs)
        for a new project called "{repo_name}". Use only the info below. No intro text,
        no numbering — output bare bullet content lines separated by newlines.

        Recent commits:
        {commit_text}

        README excerpt:
        {readme_text[:1500]}
    """).strip()
    result = ai_call(prompt)
    if not result:
        return []
    return [l.lstrip("•-– ").strip() for l in result.splitlines() if l.strip()]

# ─── 3a. Patch README ─────────────────────────────────────────────────────────
def readme_find_mentioned_repos(content):
    return set(re.findall(
        rf'github\.com/{re.escape(USERNAME)}/([A-Za-z0-9_.-]+)', content))

def readme_update_stars(content, repos):
    changed_any = False
    for r in repos:
        name, stars = r["name"], r["stargazers_count"]
        # [repo ★old]
        new, n = re.subn(rf'\[{re.escape(name)} ★(\d+)\]',
                         f'[{name} ★{stars}]', content)
        if n:
            changed_any = True
            content = new
        # badge %E2%98%85NNN
        new, n = re.subn(
            rf'({re.escape(name.replace("-","--"))}%20%E2%98%85)(\d+)',
            lambda m, s=stars: m.group(1) + str(s), content)
        if n:
            changed_any = True
            content = new
    return content, changed_any

def readme_update_repo_count(content, count):
    new = re.sub(r'Public%20Repos-\d+-', f'Public%20Repos-{count}-', content)
    return new, new != content

def readme_update_timestamp(content):
    now = datetime.now(timezone.utc).strftime("%B %Y")
    new = re.sub(r'Last Updated: [^<\n]+', f'Last Updated: {now}', content)
    return new, new != content

def readme_update_project_desc(content, repo_name, new_desc):
    """Replace the table cell description for repo_name."""
    # Table row pattern: | emoji **repo_name** | <desc> | stack | link |
    pattern = (
        rf'(\|\s*[^\|]*\*\*{re.escape(repo_name)}\*\*\s*\|)\s*[^\|]+?'
        rf'(\s*\|\s*[^\|]+\|\s*[^\|]+\|)'
    )
    new = re.sub(pattern, lambda m: f'{m.group(1)} {new_desc} {m.group(2)}', content)
    return new, new != content

def readme_insert_after(content, anchor_pattern, new_line):
    m = re.search(anchor_pattern, content)
    if m:
        pos = m.end()
        return content[:pos] + new_line + "\n" + content[pos:], True
    return content, False

# ─── 3b. Patch infographic ────────────────────────────────────────────────────
def infographic_update_stat(content, label, new_value):
    """Update a .stat-num div that precedes a .stat-label containing `label`."""
    pattern = rf'(<div class="stat-num">)\d+(<\/div>\s*<div class="stat-label">{re.escape(label)}<\/div>)'
    new = re.sub(pattern, lambda m: f'{m.group(1)}{new_value}{m.group(2)}', content)
    return new, new != content

def infographic_update_project_desc(content, proj_title, new_desc):
    """Replace proj-desc text for a given project title."""
    pattern = (
        rf'(<div class="proj-title">{re.escape(proj_title)}</div>'
        rf'.*?<div class="proj-sub">[^<]*</div>\s*<div class="proj-desc">)'
        rf'[^<]+'
        rf'(</div>)'
    )
    new = re.sub(pattern,
                 lambda m: m.group(1) + new_desc + m.group(2),
                 content, flags=re.DOTALL)
    return new, new != content

def infographic_update_cert_repos(content, count):
    new = re.sub(
        r'(GitHub · Chaitanya · )\d+( public repos)',
        lambda m: f'{m.group(1)}{count}{m.group(2)}', content)
    return new, new != content

# ─── 3c. Patch resume JSON ────────────────────────────────────────────────────
def resume_update_project_bullets(data, proj_name, new_bullets):
    for proj in data["projects"]:
        if proj["name"] == proj_name:
            proj["bullets"] = new_bullets
            return True
    return False

def resume_add_project(data, repo_name, subtitle, stack, year, bullets):
    data["projects"].append({
        "name": repo_name,
        "subtitle": subtitle,
        "stack": stack,
        "year": year,
        "bullets": bullets,
    })

# ─── 3d. Infographic — add new project card ───────────────────────────────────
NEW_CARD_TEMPLATE = """
    <!-- {name} -->
    <div class="proj-card">
      <div class="proj-top">
        <div class="proj-icon">{emoji}</div>
        <span class="proj-badge badge-ai">AI · Automation</span>
      </div>
      <div class="proj-title">{name}</div>
      <div class="proj-sub">{subtitle}</div>
      <div class="proj-desc">{desc}</div>
      <div class="proj-tags">{tags}</div>
      <div class="proj-footer"><a href="https://github.com/{username}/{repo}" class="proj-link" target="_blank" rel="noopener noreferrer">View on GitHub →</a></div>
    </div>
"""

def infographic_add_project_card(content, repo_name, subtitle, desc, stack_tags):
    # Avoid duplicates — check if a card for this repo already exists
    if f'<!-- {repo_name} -->' in content:
        return content, False
    tags_html = "".join(f'<span class="tag">{t.strip()}</span>'
                        for t in stack_tags.split("·") if t.strip())
    card = NEW_CARD_TEMPLATE.format(
        name=repo_name, subtitle=subtitle, desc=desc,
        emoji="🤖", tags=tags_html, username=USERNAME, repo=repo_name
    )
    # Insert before the anchor comment placed at end of Featured Projects grid
    marker = "    <!-- /projects-grid -->"
    if marker in content:
        return content.replace(marker, card + marker, 1), True
    return content, False

# ─── 4. Build PDF ─────────────────────────────────────────────────────────────
def build_pdf():
    log("\n── Building resume PDF ──")
    result = subprocess.run(
        [sys.executable, str(BUILD_PDF)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        log(f"  {result.stdout.strip()}")
    else:
        log(f"  [PDF build error]\n{result.stderr.strip()}")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    log("═══════════════════════════════════════════")
    log(" Chaitanya Profile Auto-Updater")
    log(f" Run at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    log("═══════════════════════════════════════════")

    # ── Load files ──────────────────────────────────────────────────────────
    readme_content     = README.read_text(encoding="utf-8")
    infographic_content = INFOGRAPHIC.read_text(encoding="utf-8")
    resume_data        = json.loads(RESUME_DATA.read_text(encoding="utf-8"))
    readme_original    = readme_content
    infographic_original = infographic_content
    resume_original    = json.dumps(resume_data, indent=2)

    # ── Fetch repos ─────────────────────────────────────────────────────────
    log("\n── Fetching repos ──")
    repos = fetch_repos()
    log(f"  {len(repos)} non-fork repos found ({sum(1 for r in repos if not r['private'])} public, {sum(1 for r in repos if r['private'])} private).")
    repo_map = {r["name"]: r for r in repos}

    # ── Star counts ─────────────────────────────────────────────────────────
    log("\n── Updating star counts ──")
    readme_content, stars_changed = readme_update_stars(readme_content, repos)
    log(f"  {'Updated' if stars_changed else 'No changes'}.")

    # ── Repo count badge ────────────────────────────────────────────────────
    log("\n── Updating public repo count ──")
    pub_count = sum(1 for r in repos if not r["private"])
    readme_content, count_changed = readme_update_repo_count(readme_content, pub_count)
    log(f"  Count: {pub_count} public {'(updated)' if count_changed else '(no change)'}.")

    infographic_content, _ = infographic_update_cert_repos(
        infographic_content, pub_count)

    # ── Detect new repos ────────────────────────────────────────────────────
    log("\n── Checking for new repos ──")
    mentioned = readme_find_mentioned_repos(readme_content)
    new_repos = [r for r in repos
                 if r["name"] not in mentioned
                 and r["name"] not in SKIP_REPOS
                 and not _DATE_IN_NAME.search(r["name"])]

    if not new_repos:
        log("  No new repos.")
    else:
        log(f"  New repos: {[r['name'] for r in new_repos]}")
        for repo in new_repos:
            name = repo["name"]
            log(f"  → Processing '{name}' …")

            # README table + overview
            table_row, overview_line = generate_new_repo_entry(repo)
            if table_row:
                readme_content, ok = readme_insert_after(
                    readme_content,
                    rf'\| 🎬 \*\*AI Content Bot\*\*[^\n]*\n',
                    table_row)
                log(f"    README table row: {'added' if ok else 'anchor missing'}.")
            if overview_line:
                readme_content, ok = readme_insert_after(
                    readme_content,
                    rf'- \*\*\[ai-content-bot\][^\n]*\n',
                    overview_line)
                log(f"    README overview line: {'added' if ok else 'anchor missing'}.")

            # Resume data
            commits  = fetch_recent_commits(name)
            readme_t = fetch_repo_readme(name)
            bullets  = generate_new_project_bullets(name, commits, readme_t)
            if bullets:
                desc = repo.get("description") or name
                stack = ", ".join(repo.get("topics", [])) or "Python"
                resume_add_project(resume_data, name, desc, stack, "2025", bullets)
                log(f"    Resume project entry added ({len(bullets)} bullets).")

            # Infographic card
            if GEMINI_KEY or ANTHROPIC_KEY:
                desc_text = (repo.get("description") or
                             f"Automated {name.replace('-',' ')} pipeline.")
                topics = repo.get("topics") or []
                stack_tags = " · ".join(topics[:6]) if topics else "Python · GitHub Actions"
                infographic_content, ok = infographic_add_project_card(
                    infographic_content, name, desc_text, desc_text, stack_tags
                )
                log(f"    Infographic card: {'added' if ok else 'already exists or anchor missing'}.")

    # ── Analyse commits for existing projects ────────────────────────────────
    if GEMINI_KEY or ANTHROPIC_KEY:
        log("\n── Analysing commits for existing projects ──")
        # Map README repo names to infographic proj titles and resume project names
        known_projects = {p["name"]: p for p in resume_data["projects"]}

        for repo in repos:
            name = repo["name"]
            if name in SKIP_REPOS or _DATE_IN_NAME.search(name) or name not in known_projects:
                continue
            commits = fetch_recent_commits(name)
            if not commits:
                continue

            proj     = known_projects[name]
            cur_desc = proj["bullets"][0] if proj["bullets"] else ""

            # Fetch file list for top commit only (to enrich the analysis)
            if commits:
                commits[0]["files"] = fetch_commit_files(name, commits[0]["sha"])

            new_desc, changed = analyse_commits_for_project(name, commits, cur_desc)
            if changed:
                log(f"  [{name}] Description updated.")
                log(f"    OLD: {cur_desc[:80]}…")
                log(f"    NEW: {new_desc[:80]}…")

                # Update resume JSON first bullet
                if proj["bullets"]:
                    proj["bullets"][0] = new_desc

                # Update README table description
                readme_content, _ = readme_update_project_desc(
                    readme_content, name, new_desc[:120])

                # Update infographic proj-desc
                infographic_content, _ = infographic_update_project_desc(
                    infographic_content, name, new_desc)
            else:
                log(f"  [{name}] No meaningful change.")
    else:
        log("\n── Skipping commit analysis (no AI key set) ──")

    # ── Timestamp ────────────────────────────────────────────────────────────
    log("\n── Updating timestamp ──")
    readme_content, ts_changed = readme_update_timestamp(readme_content)
    log(f"  {'Updated' if ts_changed else 'No change'}.")

    # ── Write files ──────────────────────────────────────────────────────────
    log("\n── Writing files ──")
    readme_written = False
    if readme_content != readme_original:
        README.write_text(readme_content, encoding="utf-8")
        readme_written = True
        log("  README.md ✓")
    else:
        log("  README.md — no changes.")

    infographic_written = False
    if infographic_content != infographic_original:
        INFOGRAPHIC.write_text(infographic_content, encoding="utf-8")
        infographic_written = True
        log("  infographic.html ✓")
    else:
        log("  infographic.html — no changes.")

    resume_written = False
    new_resume_json = json.dumps(resume_data, indent=2)
    if new_resume_json != resume_original:
        RESUME_DATA.write_text(new_resume_json, encoding="utf-8")
        resume_written = True
        log("  resume_data.json ✓")
    else:
        log("  resume_data.json — no changes.")

    # ── Rebuild PDF if any content changed ───────────────────────────────────
    if readme_written or resume_written or infographic_written:
        build_pdf()
    else:
        log("\n── No content changes — skipping PDF rebuild. ──")

    log("\n═══════════════════════════════════════════")
    log(" Done.")
    log("═══════════════════════════════════════════")


if __name__ == "__main__":
    main()
