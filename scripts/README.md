# Repository Clone Script

A robust Python-based repository clone script designed for CI/CD workflows that can handle any repository with any branch name.

## Features

- 🔄 **Smart Branch Detection**: Automatically detects available branches and falls back to default branch
- 🔐 **Token Support**: Supports GitHub tokens for private repositories
- 🧹 **Fresh Clone**: Always performs a clean clone without previous Git history
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 📊 **CI Integration**: Outputs branch info for CI consumption
- 🎯 **Branch Preference**: Supports specifying preferred branch with fallback

## Usage

### Basic Usage

```bash
python3 clone_repo.py <repository_url> <target_directory>
```

### With Preferred Branch

```bash
python3 clone_repo.py https://github.com/user/repo.git target-dir --branch main
```

### With GitHub Token (for private repos)

```bash
python3 clone_repo.py https://github.com/user/private-repo.git target-dir \
  --branch main \
  --token your_github_token \
  --use-token
```

### Environment Variables

The script also supports environment variables:

```bash
export GH_TOKEN="your_github_token"
export GITHUB_TOKEN="your_github_token"

python3 clone_repo.py https://github.com/user/repo.git target-dir --branch main
```

## Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `repo_url` | Repository URL to clone | Required |
| `target_dir` | Target directory for clone | Required |
| `--branch`, `-b` | Preferred branch name | Auto-detect |
| `--token`, `-t` | GitHub token for authentication | From environment |
| `--use-token` | Use token for authentication | Auto-detect |

## Examples

### Clone public repository (auto-detect branch)

```bash
python3 clone_repo.py https://github.com/octocat/Hello-World.git hello-world
```

### Clone private repository with token

```bash
python3 clone_repo.py https://github.com/org/private-repo.git target \
  --branch develop \
  --token $GH_TOKEN \
  --use-token
```

### Clone with environment variable

```bash
export GH_TOKEN="ghp_your_token_here"
python3 clone_repo.py https://github.com/user/repo.git target --branch main
```

## Branch Detection Logic

The script uses the following logic to determine which branch to clone:

1. **Preferred Branch**: If `--branch` is specified and exists, use that branch
2. **Default Branches**: Try common default branches in order:
   - `main`
   - `master`
   - `develop`
   - `dev`
3. **First Available**: Use the first available branch if no defaults are found
4. **Fallback**: Exit with error if no branches are found

## CI/CD Integration

The script outputs information that can be consumed by CI systems:

```bash
# Outputs for CI
::set-output name=branch::main
::set-output name=success::true
```

## Error Handling

The script handles various error scenarios:

- **Invalid Repository URL**: Exits with error
- **Branch Not Found**: Falls back to default branch
- **Authentication Issues**: Provides helpful error messages
- **Network Issues**: Reports connection problems
- **Permission Issues**: Explains access requirements

## Dependencies

This script uses only Python standard library modules:

- `os` - Environment variables
- `sys` - System exits
- `subprocess` - Command execution
- `argparse` - Command line parsing
- `pathlib` - Path handling

**No external dependencies required!**

## Security Notes

- Tokens are only used when explicitly requested via `--use-token` or environment variable
- Tokens are stripped from logs and error messages
- The script does not store or cache tokens
- All subprocess calls use proper shell escaping

## Troubleshooting

### "Branch not found" error

The script will automatically fall back to the default branch. Check the logs to see which branch was actually cloned.

### "Authentication failed" for private repos

Make sure you have:
1. A valid GitHub token with appropriate permissions
2. The `--use-token` flag is set
3. The token is passed via `--token` or environment variable

### "Repository not found"

Verify:
1. The repository URL is correct
2. You have access to the repository
3. The repository exists

### "Clone failed" with no details

This usually indicates a network issue or permission problem. Check your internet connection and permissions.

## Output Examples

### Successful Clone

```
🔍 Cloning target repository: https://github.com/user/repo.git
🔍 Checking available branches...
📋 Available branches: main, master, develop
🎯 Using specified branch: main
🔍 Cloning repository: https://github.com/user/repo.git
📌 Branch: main
📁 Target directory: target-dir
✅ Successfully cloned branch: main
🎉 Repository cloned successfully!
📂 Location: /path/to/target-dir
📝 Latest commit: abc123 Add new feature
```

### Branch Not Found

```
🔍 Cloning target repository: https://github.com/user/repo.git
🔍 Checking available branches...
📋 Available branches: master, develop
⚠️  Preferred branch 'main' not found, using default branch
🎯 Using default branch: master
🔍 Cloning repository: https://github.com/user/repo.git
📌 Branch: master
📁 Target directory: target-dir
✅ Successfully cloned branch: master
🎉 Repository cloned successfully!
```

## License

This script is provided as-is for use in CI/CD workflows.