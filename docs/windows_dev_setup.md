# Windows Development Setup

This guide covers how to configure a semi-autonomous workflow on Windows 10 using
VS Code, WSL and GitHub Actions. The steps mirror the Unix instructions in the
other documents while highlighting Windows specific tips.

## 1. Editors and environment

- **Visual Studio Code** is recommended for Python and JavaScript/TypeScript.
  Install the official extensions and use the integrated terminal for Git.
- **WSL (Windows Subsystem for Linux)** provides a Unix-like shell and is fully
  supported by VS Code. It allows switching Python interpreters and creating
  virtual environments just like on Linux.
- Install the latest **Node.js LTS** and enable `pip`/`venv` for Python. These
  tools are required by the front-end and back-end.

## 2. Git workflow

1. Initialize a local Git repository or clone the existing one.
2. Work on feature branches for major changes and keep Pull Requests small and
   focused.
3. Describe each PR clearly to help reviewers understand the purpose.

## 3. Continuous Integration

The project uses GitHub Actions to lint and test both the Node.js front‑end and
Python back‑end. Below is a simplified example of the workflow:

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with:
      node-version: '18.x'
  - run: npm ci
  - run: npm run lint
  - run: npm run build --if-present
  - run: npm test
  - uses: actions/setup-python@v5
    with:
      python-version: '3.10'
  - run: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt -r requirements-dev.txt
  - run: flake8 .
  - run: pytest
```

Use the above as a starting point when customising `.github/workflows/` for your
Windows setup. The same configuration runs on Linux via WSL or the CI servers.
