# Security

Kavazi copies files into a target repository and validates local records. Adoption should preserve existing work, reject unsafe paths, and report conflicts before writes. A failure of those boundaries deserves careful investigation.

## Report a vulnerability privately

Open [Kavazi Method on GitHub](https://github.com/Cyber-preacher/kavazi-method) and use **Security → Report a vulnerability** if that option is available. Enabling and verifying private reporting is part of the first release preparation; this document does not yet establish that it is enabled. If the option is unavailable, ask `@Cyber-preacher` for a private reporting channel without posting vulnerability details publicly. No reporting email address is designated.

Include the affected version or revision, Python version and platform, a minimal reproduction using non-sensitive files, the observed behavior, and the potential impact. Do not include credentials, private repository content, or personal data. Please allow coordination before publishing exploit details.

Ordinary bugs and feature requests belong in the [issue tracker](https://github.com/Cyber-preacher/kavazi-method/issues). If a problem might expose or alter another project's data, begin with private reporting.

## Support and scope

The first `0.1.0` release is in preparation. There is no promised response time or backport policy. Verified release information belongs in [CHANGELOG](CHANGELOG.md).

The CLI checks records and controlled file operations. It cannot authenticate the author of an approval, prove that an entered test result is true, or prevent an agent with direct file access from bypassing instructions. Review project changes and run meaningful checks within the host's existing permissions.
