# Claude AI Assistant Instructions

## 🚨 CRITICAL: Git Pager Configuration

**ALWAYS use `--no-pager` option with git commands that can trigger paging!**

### Required Git Command Format

```bash
# ✅ CORRECT - Use these formats
git --no-pager diff [options]
git --no-pager log [options]
git --no-pager show [options]
git --no-pager blame [options]

# ❌ WRONG - These will cause hanging/pausing
git diff [options]
git log [options]
git show [options]
git blame [options]
```

### Why This Matters

Git commands like `diff`, `log`, `show`, and `blame` automatically use a pager (like `less` or `more`) to display output. In automated environments, this causes:
- Commands to hang waiting for user input
- Execution to pause indefinitely
- Timeouts and failed operations

### Safe Git Commands (No Pager Issues)

These commands typically don't trigger pagers and are safe to use normally:
```bash
git status
git add [files]
git commit [options]
git push [options]
git pull [options]
git branch [options]
git checkout [options]
```

### Alternative: Set Environment Variable

If you need to run multiple git commands, you can also set:
```bash
# For PowerShell/CMD
$env:GIT_PAGER = ""
git diff  # Now safe

# For bash/sh
export GIT_PAGER=""
git diff  # Now safe
```

## 🔥 REMEMBER: Always use `git --no-pager` for diff, log, show, blame commands!