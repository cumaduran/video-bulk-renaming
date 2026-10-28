# Release checklist

- [ ] Confirm unit tests pass on Windows and Linux.
- [ ] Build the application on `windows-latest` using the GitHub Actions workflow.
- [ ] Download and manually test the EXE on a real Windows 10/11 machine.
- [ ] Rename and undo a **backup copy** of representative media files.
- [ ] Review translations, documentation, and the application icon.
- [ ] Review PySide6/Qt LGPL obligations (notices, licensing, replaceable libraries as applicable) before redistributing binaries.
- [ ] Sign the executable for public distribution if a trusted signing certificate is available.
- [ ] Publish with **Actions → Build Windows EXE → Run workflow → Release tag: v1.0.0**, or by pushing `git tag v1.0.0 && git push origin v1.0.0`.
- [ ] Confirm the release contains `EpisodeFlow.exe`, `EpisodeFlow-Windows.zip`, and `SHA256SUMS.txt` and is downloadable on the **Releases** page.
- [ ] Verify the publisher credit and clickable [@cumaduran](https://github.com/cumaduran) link in the app footer and About dialog.
