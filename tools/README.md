# Optional external tools

AETHERVEXA works without these, but they add a lot:

| Tool | What it adds |
|---|---|
| ExifTool | Thousands of extra metadata tags, including maker notes |
| c2patool | Cryptographic validation of Content Credentials (C2PA); when online, signers are checked against the official C2PA trust list |

**Easiest:** in AETHERVEXA open **Settings → External tools** and press **Install**. AETHERVEXA downloads the official release (ExifTool from exiftool.org/SourceForge, c2patool from GitHub), verifies the published SHA-256 checksum and installs it into `%LOCALAPPDATA%\AETHERVEXA\tools`. No administrator rights are needed.

**Other ways AETHERVEXA finds them**, in order: the path set in Settings, a `tools` folder next to `AETHERVEXA.exe`, `%LOCALAPPDATA%\AETHERVEXA\tools`, then your `PATH` (including `winget install OliverBetz.ExifTool`).

If you download ExifTool by hand, rename `exiftool(-k).exe` to `exiftool.exe` and keep its `exiftool_files` folder beside it. The `(-k)` makes ExifTool wait for a key press, so AETHERVEXA will not run it under that name.

How they are run:

- **ExifTool** receives the file contents through standard input, so it never sees or opens the original file.
- **c2patool** is given a private temporary copy, which is deleted straight afterwards.
