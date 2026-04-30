---
name: github-repo-management
description: "Clone/create/fork repos; manage remotes, releases."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Repositories, Git, Releases, Secrets, Configuration]
    related_skills: [github-auth, github-pr-workflow, github-issues]
---

# GitHub Repository Management

Create, clone, fork, configure, and manage GitHub repositories. Each section shows `gh` first, then the `git` + `curl` fallback.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)

### Setup

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

# Get your GitHub username (needed for several operations)
if [ "$AUTH" = "gh" ]; then
  GH_USER=$(gh api user --jq '.login')
else
  GH_USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin)['login'])")
fi
```

If you're inside a repo already:

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## Publishing a Local Checkpoint to a Diverged Remote

Use this when a user asks to push a large local checkpoint and `git push` is rejected
because the target branch has remote-only commits, or the remote appears to have
been initialized independently from the local repository.

1. Inspect before pushing; never assume `origin` is the desired remote when a fork
   or renamed product repo exists:

```bash
git status --short
git branch --show-current
git remote -v
git fetch <remote> <branch>
git rev-list --left-right --count HEAD...<remote>/<branch>
git log --oneline HEAD..<remote>/<branch> | sed -n '1,40p'
git log --oneline <remote>/<branch>..HEAD | sed -n '1,40p'
```

2. If histories are unrelated or the remote branch has intentional commits that
   must be preserved, avoid `--force` unless the user explicitly asks to overwrite
   the remote. A safe checkpoint pattern is to create a publish branch based on
   the remote tip, then replace its tree with the reviewed local checkpoint:

```bash
LOCAL_CHECKPOINT=$(git rev-parse HEAD)
git switch -c publish/checkpoint <remote>/<branch>
git read-tree --reset -u "$LOCAL_CHECKPOINT"
git status --short
git diff --cached --stat
# Re-run cheap checks such as git diff --cached --check before committing.
git commit -m "chore: checkpoint <summary>"
git push <remote> publish/checkpoint:<branch>
```

This creates a normal fast-forward commit on the remote branch while preserving
remote-only commits. After push, align local main if appropriate:

```bash
git fetch <remote> <branch>
git switch main
git reset --hard <remote>/<branch>
git branch --set-upstream-to=<remote>/<branch> main
```

3. If a large HTTPS push fails with `RPC failed; HTTP 400`,
`send-pack: unexpected disconnect`, or `fatal: the remote end hung up
unexpectedly`, retry once with Git HTTP/1.1 and a larger post buffer:

```bash
git config http.version HTTP/1.1
git config http.postBuffer 524288000
git push <remote> <local-branch>:<remote-branch>
```

4. Verify the result:

```bash
git fetch <remote> <branch>
git rev-parse <remote>/<branch>
git rev-parse HEAD
git status --short --branch
```

---

## 1. Cloning Repositories

Cloning is pure `git` — works identically either way:

```bash
# Clone via HTTPS (works with credential helper or token-embedded URL)
git clone https://github.com/owner/repo-name.git

# Clone into a specific directory
git clone https://github.com/owner/repo-name.git ./my-local-dir

# Shallow clone (faster for large repos)
git clone --depth 1 https://github.com/owner/repo-name.git

# Clone a specific branch
git clone --branch develop https://github.com/owner/repo-name.git

# Clone via SSH (if SSH is configured)
git clone git@github.com:owner/repo-name.git
```

**With gh (shorthand):**

```bash
gh repo clone owner/repo-name
gh repo clone owner/repo-name -- --depth 1
```

## Publishing a new local repo when `gh` is not logged in

Use this when the user asks to “push/upload to GitHub” from a local repo that has no remote, `gh auth status` is not authenticated, but HTTPS git credentials exist. This pattern avoids printing tokens.

1. Inspect local state and auth without exposing secrets:

```bash
git status --short --branch
git remote -v
git branch --show-current
if [ -n "$GITHUB_TOKEN" ]; then echo GITHUB_TOKEN_PRESENT; else echo GITHUB_TOKEN_MISSING; fi
printf 'protocol=https\nhost=github.com\n\n' | git credential fill 2>/dev/null | sed -n 's/^username=/GIT_USERNAME=/p; s/^password=.*/GIT_CREDENTIAL_PRESENT/p'
```

2. Resolve the account via GitHub API using `git credential fill`, but never echo the password/token:

```bash
python3 - <<'PY'
import json, subprocess, urllib.request
cred=subprocess.run(['git','credential','fill'], input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True, check=True).stdout
items=dict(line.split('=',1) for line in cred.splitlines() if '=' in line)
token=items.get('password')
req=urllib.request.Request('https://api.github.com/user', headers={'Authorization': f'token {token}', 'Accept':'application/vnd.github+json'})
with urllib.request.urlopen(req, timeout=20) as r:
    print('login='+json.load(r)['login'])
PY
```

3. If the target repo does not exist and the user did not specify visibility, prefer private for a work-in-progress checkpoint. Create it, add `origin`, push, and verify SHA parity:

```bash
TARGET_OWNER=<login>
TARGET_REPO=<repo-name>
python3 - <<'PY'
import json, os, subprocess, urllib.request, urllib.error
owner=os.environ['TARGET_OWNER']; repo=os.environ['TARGET_REPO']
cred=subprocess.run(['git','credential','fill'], input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True, check=True).stdout
items=dict(line.split('=',1) for line in cred.splitlines() if '=' in line)
token=items.get('password')
payload=json.dumps({'name': repo, 'private': True, 'auto_init': False}).encode()
req=urllib.request.Request('https://api.github.com/user/repos', data=payload, method='POST', headers={'Authorization': f'token {token}', 'Accept':'application/vnd.github+json', 'Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=30) as r:
    d=json.load(r)
print('created='+d['full_name'])
print('private='+str(d['private']).lower())
print('html_url='+d['html_url'])
PY

git remote add origin "https://github.com/$TARGET_OWNER/$TARGET_REPO.git"
git push -u origin "$(git branch --show-current)"
git fetch origin "$(git branch --show-current)"
echo local=$(git rev-parse HEAD)
echo remote=$(git rev-parse "origin/$(git branch --show-current)")
git status --short --branch
```

## 2. Creating Repositories

**With gh:**

```bash
# Create a public repo and clone it
gh repo create my-new-project --public --clone

# Private, with description and license
gh repo create my-new-project --private --description "A useful tool" --license MIT --clone

# Under an organization
gh repo create my-org/my-new-project --public --clone

# From existing local directory
cd /path/to/existing/project
gh repo create my-project --source . --public --push
```

**With git + curl:**

```bash
# Create the remote repo via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{
    "name": "my-new-project",
    "description": "A useful tool",
    "private": false,
    "auto_init": true,
    "license_template": "mit"
  }'

# Clone it
git clone https://github.com/$GH_USER/my-new-project.git
cd my-new-project

# -- OR -- push an existing local directory to the new repo
cd /path/to/existing/project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/$GH_USER/my-new-project.git
git push -u origin main
```

To create under an organization:

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/orgs/my-org/repos \
  -d '{"name": "my-new-project", "private": false}'
```

### From a Template

**With gh:**

```bash
gh repo create my-new-app --template owner/template-repo --public --clone
```

**With curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/template-repo/generate \
  -d '{"owner": "'"$GH_USER"'", "name": "my-new-app", "private": false}'
```

## 3. Forking Repositories

**With gh:**

```bash
gh repo fork owner/repo-name --clone
```

**With git + curl:**

```bash
# Create the fork via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo-name/forks

# Wait a moment for GitHub to create it, then clone
sleep 3
git clone https://github.com/$GH_USER/repo-name.git
cd repo-name

# Add the original repo as "upstream" remote
git remote add upstream https://github.com/owner/repo-name.git
```

### Publishing an existing local OSS worktree to the user's fork

Use this when the user has an existing local checkout/worktree based on an upstream open-source repo, has created a GitHub fork (possibly with a different repo name), and wants the current local branch pushed to that fork. Do not assume the current `origin` is safe: it may still point at the upstream official repo.

1. Verify the target repo and license/visibility before touching remotes:

```bash
TARGET_OWNER=your-user
TARGET_REPO=your-fork
python - <<'PY'
import json, os, urllib.request
owner=os.environ['TARGET_OWNER']; repo=os.environ['TARGET_REPO']
with urllib.request.urlopen(f'https://api.github.com/repos/{owner}/{repo}', timeout=20) as r:
    d=json.load(r)
print('full_name=', d.get('full_name'))
print('private=', d.get('private'))
print('fork=', d.get('fork'))
print('license=', d.get('license'))
print('html_url=', d.get('html_url'))
PY
```

2. Audit local state and never stage runtime secrets or local homes:

```bash
git status --short --branch
git remote -v
git ls-files --others --exclude-standard | sed -n '1,160p'
git status --ignored --short | grep -Ei '(auth\.json|\.env|secret|token|credential|state\.db|logs/|test-homes|feishu-accounts)' || true
git diff --check
```

Only stage source, tests, docs, and intended helper scripts. Avoid staging `.env`, `auth.json`, `state.db`, logs, profile/test-home directories, credential JSON, or local `.hermes/` runtime/planning directories unless explicitly intended and reviewed.

3. Stage intended files, scan the staged diff, run focused tests, then commit:

```bash
git add <intended files only>
git diff --cached --stat
git diff --cached --name-only | grep -Ei '(^|/)(\.env|auth\.json|state\.db|.*secret.*|.*token.*|logs/|test-homes/|feishu-accounts/)' && {
  echo 'Refusing: staged path looks sensitive'; exit 1;
} || true
git diff --cached --check
# Run the project's relevant focused tests here, e.g. python -m pytest ... -q
git commit -m "feat: concise summary"
```

4. Rewire remotes so the fork is `origin` and the official repo is `upstream`:

```bash
UPSTREAM_URL=https://github.com/original-owner/original-repo.git
FORK_URL=https://github.com/$TARGET_OWNER/$TARGET_REPO.git

if git remote get-url upstream >/dev/null 2>&1; then
  :
elif [ "$(git remote get-url origin)" = "$UPSTREAM_URL" ]; then
  git remote rename origin upstream
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$FORK_URL"
else
  git remote add origin "$FORK_URL"
fi

git remote -v
```

5. Push the current branch to the fork and verify by commit SHA:

```bash
BRANCH=$(git branch --show-current)
git push -u origin "$BRANCH"
git fetch origin "$BRANCH"
echo local=$(git rev-parse HEAD)
echo remote=$(git rev-parse "origin/$BRANCH")
git status --short --branch
```

Optionally verify via GitHub API without `gh`:

```bash
python - <<'PY'
import json, os, subprocess, urllib.request
owner=os.environ['TARGET_OWNER']; repo=os.environ['TARGET_REPO']
branch=subprocess.check_output(['git','branch','--show-current'], text=True).strip()
with urllib.request.urlopen(f'https://api.github.com/repos/{owner}/{repo}/commits/{branch}', timeout=20) as r:
    d=json.load(r)
print('sha=', d['sha'])
print('url=', d['html_url'])
print('message=', d['commit']['message'].split('\n')[0])
PY
```

### Keeping a Fork in Sync

```bash
# Pure git — works everywhere
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**With gh (shortcut):**

```bash
gh repo sync $GH_USER/repo-name
```

## 4. Repository Information

**With gh:**

```bash
gh repo view owner/repo-name
gh repo list --limit 20
gh search repos "machine learning" --language python --sort stars
```

**With curl:**

```bash
# View repo details
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO \
  | python3 -c "
import sys, json
r = json.load(sys.stdin)
print(f\"Name: {r['full_name']}\")
print(f\"Description: {r['description']}\")
print(f\"Stars: {r['stargazers_count']}  Forks: {r['forks_count']}\")
print(f\"Default branch: {r['default_branch']}\")
print(f\"Language: {r['language']}\")"

# List your repos
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/user/repos?per_page=20&sort=updated" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    vis = 'private' if r['private'] else 'public'
    print(f\"  {r['full_name']:40}  {vis:8}  {r.get('language', ''):10}  ★{r['stargazers_count']}\")"

# Search repos
curl -s \
  "https://api.github.com/search/repositories?q=machine+learning+language:python&sort=stars&per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin)['items']:
    print(f\"  {r['full_name']:40}  ★{r['stargazers_count']:6}  {r['description'][:60] if r['description'] else ''}\")"
```

## 5. Repository Settings

**With gh:**

```bash
gh repo edit --description "Updated description" --visibility public
gh repo edit --enable-wiki=false --enable-issues=true
gh repo edit --default-branch main
gh repo edit --add-topic "machine-learning,python"
gh repo edit --enable-auto-merge
```

**With curl:**

```bash
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO \
  -d '{
    "description": "Updated description",
    "has_wiki": false,
    "has_issues": true,
    "allow_auto_merge": true
  }'

# Update topics
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.mercy-preview+json" \
  https://api.github.com/repos/$OWNER/$REPO/topics \
  -d '{"names": ["machine-learning", "python", "automation"]}'
```

## 6. Branch Protection

```bash
# View current protection
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection

# Set up branch protection
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["ci/test", "ci/lint"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1
    },
    "restrictions": null
  }'
```

## 7. Secrets Management (GitHub Actions)

**With gh:**

```bash
gh secret set API_KEY --body "your-secret-value"
gh secret set SSH_KEY < ~/.ssh/id_rsa
gh secret list
gh secret delete API_KEY
```

**With curl:**

Secrets require encryption with the repo's public key — more involved via API:

```bash
# Get the repo's public key for encrypting secrets
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/public-key

# Encrypt and set (requires Python with PyNaCl)
python3 -c "
from base64 import b64encode
from nacl import encoding, public
import json, sys

# Get the public key
key_id = '<key_id_from_above>'
public_key = '<base64_key_from_above>'

# Encrypt
sealed = public.SealedBox(
    public.PublicKey(public_key.encode('utf-8'), encoding.Base64Encoder)
).encrypt('your-secret-value'.encode('utf-8'))
print(json.dumps({
    'encrypted_value': b64encode(sealed).decode('utf-8'),
    'key_id': key_id
}))"

# Then PUT the encrypted secret
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/API_KEY \
  -d '<output from python script above>'

# List secrets (names only, values hidden)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets \
  | python3 -c "
import sys, json
for s in json.load(sys.stdin)['secrets']:
    print(f\"  {s['name']:30}  updated: {s['updated_at']}\")"
```

Note: For secrets, `gh secret set` is dramatically simpler. If setting secrets is needed and `gh` isn't available, recommend installing it for just that operation.

## 8. Releases

**With gh:**

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release create v2.0.0-rc1 --draft --prerelease --generate-notes
gh release create v1.0.0 ./dist/binary --title "v1.0.0" --notes "Release notes"
gh release list
gh release download v1.0.0 --dir ./downloads
```

**With curl:**

If `gh` is unavailable but HTTPS git push works, first try to reuse the configured git credential without printing it:

```bash
if [ -z "$GITHUB_TOKEN" ]; then
  GITHUB_TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' \
    | git credential fill 2>/dev/null \
    | sed -n 's/^password=//p' \
    | head -1)
fi
[ -n "$GITHUB_TOKEN" ] || { echo "No GitHub token available"; exit 1; }
```

Create/push the tag before creating the release:

```bash
git tag -a v1.0.0 -m "v1.0.0"
git push origin v1.0.0
```

If tag push fails with a transient TLS/HTTP error such as `SSL_ERROR_SYSCALL`, retry once with the same transport workaround used for large pushes:

```bash
git config http.version HTTP/1.1
git config http.postBuffer 524288000
git push origin v1.0.0
```

Create a release:

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/releases \
  -d '{
    "tag_name": "v1.0.0",
    "name": "v1.0.0",
    "body": "## Changelog\n- Feature A\n- Bug fix B",
    "draft": false,
    "prerelease": false,
    "generate_release_notes": true
  }'
```

curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/releases \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    tag = r.get('tag_name', 'no tag')
    print(f\"  {tag:15}  {r['name']:30}  {'draft' if r['draft'] else 'published'}\")"

# Upload a release asset (binary file)
RELEASE_ID=<id_from_create_response>
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  "https://uploads.github.com/repos/$OWNER/$REPO/releases/$RELEASE_ID/assets?name=binary-amd64" \
  --data-binary @./dist/binary-amd64
```

## 9. GitHub Actions Workflows

**With gh:**

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID>
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID>
gh run rerun <RUN_ID> --failed
gh workflow run ci.yml --ref main
gh workflow run deploy.yml -f environment=staging
```

**With curl:**

```bash
# List workflows
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows \
  | python3 -c "
import sys, json
for w in json.load(sys.stdin)['workflows']:
    print(f\"  {w['id']:10}  {w['name']:30}  {w['state']}\")"

# List recent runs
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin)['workflow_runs']:
    print(f\"  Run {r['id']}  {r['name']:30}  {r['conclusion'] or r['status']}\")"

# Download failed run logs
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs

# Re-run a failed workflow
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun

# Re-run only failed jobs
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun-failed-jobs

# Trigger a workflow manually (workflow_dispatch)
WORKFLOW_ID=<workflow_id_or_filename>
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_ID/dispatches \
  -d '{"ref": "main", "inputs": {"environment": "staging"}}'
```

## 10. Gists

**With gh:**

```bash
gh gist create script.py --public --desc "Useful script"
gh gist list
```

**With curl:**

```bash
# Create a gist
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/gists \
  -d '{
    "description": "Useful script",
    "public": true,
    "files": {
      "script.py": {"content": "print(\"hello\")"}
    }
  }'

# List your gists
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/gists \
  | python3 -c "
import sys, json
for g in json.load(sys.stdin):
    files = ', '.join(g['files'].keys())
    print(f\"  {g['id']}  {g['description'] or '(no desc)':40}  {files}\")"
```

## Quick Reference Table

| Action | gh | git + curl |
|--------|-----|-----------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `curl POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `curl POST /repos/o/r/forks` + `git clone` |
| Repo info | `gh repo view o/r` | `curl GET /repos/o/r` |
| Edit settings | `gh repo edit --...` | `curl PATCH /repos/o/r` |
| Create release | `gh release create v1.0` | `curl POST /repos/o/r/releases` |
| List workflows | `gh workflow list` | `curl GET /repos/o/r/actions/workflows` |
| Rerun CI | `gh run rerun ID` | `curl POST /repos/o/r/actions/runs/ID/rerun` |
| Set secret | `gh secret set KEY` | `curl PUT /repos/o/r/actions/secrets/KEY` (+ encryption) |
