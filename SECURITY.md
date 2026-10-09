# Security

Kavazi copies files into a target repository and validates local records. Adoption should preserve existing work, reject unsafe paths, and report conflicts before writes. A failure of those boundaries deserves careful investigation.

## Report a vulnerability privately

If this repository is hosted on GitHub and its **Security → Report a vulnerability** option is available, use it. Otherwise, ask the maintainer for a private reporting channel without posting vulnerability details publicly. This checkout does not designate an email address or establish that private reporting has been enabled.

Include the affected version or revision, Python version and platform, a minimal reproduction using non-sensitive files, the observed behavior, and the potential impact. Do not include credentials, private repository content, or personal data. Please allow coordination before publishing exploit details.

Ordinary bugs and feature requests can use the repository's issue tracker when available. If a problem might expose or alter another project's data, begin with private reporting.

## Support and scope

The package currently declares version `0.1.0` and has no published release or maintenance schedule recorded in this checkout. There is no promised response time or backport policy. Verified release information belongs in [CHANGELOG](CHANGELOG.md).

The CLI checks records and controlled file operations. It cannot authenticate the author of an approval, prove that an entered test result is true, or prevent an agent with direct file access from bypassing instructions. Review project changes and run meaningful checks within the host's existing permissions.
