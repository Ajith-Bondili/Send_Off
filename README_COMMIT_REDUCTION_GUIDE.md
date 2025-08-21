# Git Commit Reduction Guide

## Problem: GitHub Overcounting Contributions

When you rewrite Git history (rebase, squash, force-push), GitHub can overcount contributions. The only reliable fix is to **delete and recreate the repository**.

**Reference:** [GitHub Community Discussion #59921](https://github.com/orgs/community/discussions/59921)

---

## Solution: Delete/Recreate + Filter Commits

### Prerequisites
```bash
# Install git-filter-repo (one-time setup)
pip install git-filter-repo
```

---

## Step-by-Step Process

### Phase 1: Backup & Measure (Safety First)

```bash
# 1. Create local backup
cd /path/to/your/repo
git fetch --all --tags
git branch backup/pre-reduction-$(date +%Y%m%d%H%M%S)

# 2. Optional: Create mirror backup
cd ..
git clone --mirror /path/to/your/repo YourRepo_mirror_backup

# 3. Measure current commits since target date
cd /path/to/your/repo
git log --oneline --since="2025-01-02" | wc -l
# Note this number - should be roughly halved after process
```

### Phase 2: GitHub Repository Reset (You Do This)

**Delete existing repo:**
1. Go to: `https://github.com/YourUsername/YourRepo/settings`
2. Scroll to bottom → "Delete this repository"
3. Type repo name to confirm
4. Click "I understand, delete this repository"

**Create new repo:**
1. Go to: `https://github.com/new`
2. Name: `YourNewRepoName` (can be same or different)
3. Keep it **public** (or private, your choice)
4. **IMPORTANT:** Don't initialize with README/gitignore (keep empty)
5. Click "Create repository"

### Phase 3: Reduce Commits (Automated)

```bash
cd /path/to/your/local/repo

# Method 1: Drop every 2nd commit that touches specific file since date
git filter-repo --force --commit-callback '
import datetime
commit_date_str = commit.author_date.decode()
try:
    commit_timestamp = int(commit_date_str.split()[0])
    commit_date = datetime.datetime.fromtimestamp(commit_timestamp)
    cutoff_date = datetime.datetime(2025, 1, 2)  # ADJUST THIS DATE
    
    if commit_date >= cutoff_date:
        # ADJUST THIS FILE NAME for your bot
        if b"commit_bot.txt" in commit.file_changes:
            hash_int = int(commit.original_id.hex()[-2:], 16)
            if hash_int % 2 == 0:  # Drop every 2nd commit
                commit.skip()
except:
    pass  # Keep commits we cannot parse
'

# Method 2: Drop every 2nd commit by specific author since date
git filter-repo --force --commit-callback '
import datetime
commit_date_str = commit.author_date.decode()
if commit.author_email == b"your-email@example.com":  # ADJUST EMAIL
    try:
        commit_timestamp = int(commit_date_str.split()[0])
        commit_date = datetime.datetime.fromtimestamp(commit_timestamp)
        cutoff_date = datetime.datetime(2025, 1, 2)  # ADJUST DATE
        
        if commit_date >= cutoff_date:
            hash_int = int(commit.original_id.hex()[-2:], 16)
            if hash_int % 2 == 0:
                commit.skip()
    except:
        pass
'
```

### Phase 4: Verify & Push

```bash
# 1. Verify reduction
git log --oneline --since="2025-01-02" | wc -l
# Should be roughly half the original number

# 2. Set new remote URL
git remote set-url origin https://github.com/YourUsername/YourNewRepoName.git

# 3. Push cleaned history
git push -u origin main
```

### Phase 5: Verification

```bash
# Verify remote matches local
git fetch origin
git log origin/main --oneline --since="2025-01-02" | wc -l
```

---

## Rollback (If Needed)

```bash
# Reset to backup branch
git reset --hard backup/pre-reduction-YYYYMMDDHHMMSS
git push --force-with-lease origin main

# Or restore from mirror
cd /path/to/YourRepo_mirror_backup
git push --force-with-lease origin refs/heads/main:refs/heads/main
```

---

## Customization Variables

### Dates
```python
cutoff_date = datetime.datetime(2025, 1, 2)  # Start reducing from this date
```

### Target Files (for bot commits)
```python
if b"commit_bot.txt" in commit.file_changes:  # Only commits touching this file
if b"output.log" in commit.file_changes:     # Alternative file
```

### Author Filtering
```python
if commit.author_email == b"bot@example.com":     # Only bot commits
if commit.author_email == b"your@email.com":      # Only your commits
```

### Reduction Ratios
```python
if hash_int % 2 == 0:    # Keep 1 out of 2 (50% reduction)
if hash_int % 3 == 0:    # Keep 2 out of 3 (33% reduction)  
if hash_int % 4 == 0:    # Keep 3 out of 4 (25% reduction)
```

---

## Why This Works

1. **GitHub overcounting fix:** Delete/recreate resets GitHub's internal contribution tracking
2. **Commit reduction:** `git filter-repo` permanently removes commits from history
3. **Consistent selection:** Using commit hash ensures same commits are always dropped
4. **Date filtering:** Only affects commits after your specified cutoff date
5. **File filtering:** Only targets bot-generated commits, preserves real work

---

## Alternative: Simple Interactive Rebase (Small Repos)

For repos with fewer commits, you can use interactive rebase:

```bash
# Find base commit before your cutoff
BASE=$(git rev-list -1 --before="2025-01-02 00:00:00" main)

# Interactive rebase - manually change 'pick' to 'drop' for unwanted commits
git rebase -i $BASE

# Force push
git push --force-with-lease origin main
```

---

## Prevention: Reduce Future Bot Commits

### Option 1: Lower commit frequency
```python
# In your bot script
MAX_COMMITS = 3  # Instead of 6
NO_COMMIT_CHANCE = 0.7  # 70% chance to skip
```

### Option 2: Batch commits
```python
# Write multiple entries, commit once
for i in range(commits):
    entries.append(generate_content())
if entries:
    write_all_entries(entries)
    git_commit_once()
```

### Option 3: Disable bot entirely
```bash
# Comment out cron job
crontab -e
# Add # in front of bot line

# Disable GitHub Actions
# Comment out schedule in .github/workflows/
```

---

## Success Indicators

✅ **GitHub contribution graph shows reduced numbers**  
✅ **Local commit count roughly halved since cutoff date**  
✅ **Remote commit count matches local**  
✅ **All important files preserved**  
✅ **No "new" contributions added to today's date**

---

## Notes

- Process takes 5-10 minutes depending on repo size
- GitHub contribution graph updates within 1 hour
- Always test on a copy/branch first if unsure
- Keep backups until you're satisfied with results
- This method is **irreversible** once pushed (use backups to restore)

---

*Last updated: $(date)*
