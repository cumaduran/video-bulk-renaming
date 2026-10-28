# Security policy

EpisodeFlow works offline and uses local filesystem access selected by the user. It is not designed to analyze untrusted video contents.

- Always preview proposed filenames.
- The application avoids overwriting existing files and skips uncertain episode numbers.
- A crash or power failure can interrupt a multi-file rename. Keep backups of important data.
- Undo requires the latest saved journal and unchanged destination paths.
- Do not run downloaded unsigned executables from untrusted sources. Prefer GitHub Actions artifacts produced from source you have reviewed.

To privately report a security issue, use GitHub's **Private vulnerability reporting** feature if it is enabled for the repository. Do not include sensitive local paths or sample video content in public issues.
