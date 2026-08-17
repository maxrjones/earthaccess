# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Common Changelog](https://common-changelog.org/)
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
`earthaccess-auth` is released in lockstep with
[earthaccess](https://github.com/earthaccess-dev/earthaccess) — see its
[changelog](../CHANGELOG.md) for the rest of the project.

## [Unreleased]

### Added

- Initial release. Extracted from `earthaccess`: EDL login (`login`, `Auth`),
  the DAAC registry, systems (`PROD`/`UAT`), and the two login exceptions.
  Optional `fsspec` and `obstore` extras add an authenticated HTTPS session
  and an S3 credential provider, respectively.
  ([#XXXX](https://github.com/earthaccess-dev/earthaccess/pull/XXXX))

[Unreleased]: https://github.com/earthaccess-dev/earthaccess/compare/v0.18.0...HEAD
