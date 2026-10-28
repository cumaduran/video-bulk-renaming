# Contributing

Thanks for improving EpisodeFlow! Keep changes focused, readable, and safe for users' data.

1. Fork the repository, create a feature branch, and install `requirements-dev.txt` in a virtual environment.
2. Add regression tests for new detection rules. Do **not** make ambiguous filenames silently rename.
3. Run `python -m pytest -q` before opening a pull request.
4. Update **all** translations when introducing a new UI string. Each locale must provide the same keys.
5. Do not commit video content, personal filesystem paths, credentials, `.exe` binaries, temporary files, or undo history.
6. Explain behavior changes and potential compatibility issues in the pull request.

Please report bugs with **sanitized example filenames only**, not personal folder paths.
