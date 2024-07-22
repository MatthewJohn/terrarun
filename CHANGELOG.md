# Changelog

## [0.54.1](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.54.0...v0.54.1) (2024-07-22)


### Bug Fixes

* Add mock run-events endpoint to fix compatibility with Terraform 1.5 ([bcdbf6d](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/bcdbf6d151c81f5c7bbb05682ec13ffb46959a05)), closes [#143](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/143)
* **api:** Clear expired objects on flask connection completion - the agent job API appeared to be keeping cached objects with old statuses ([bb6dfab](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/bb6dfab94fdd2c4972283204e666c5b51983ae2c))
* **api:** Fix API response to always include 'included' attribute if includes have been requested, even if there are no included objects to return ([1419f89](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/1419f89cc8247e415d0d94202f82228dbaf2759f))
* Fix error when attempting to modify project settings and VCS is not configured ([11ba55c](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/11ba55cd773ddc04b74ed5c75fb5383c3b876679))
* Fix werzerg package version to avoid import errors for url_prase ([0c504da](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/0c504daf6e309dd7a29925cc287c6bc9721be431))
* return error to Terraform when Terraform version is not set or set to wrong version ([44ad989](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/44ad98921ccc9f59e18e939e41608ba5f7a5aeff))
* **ui:** Handle re-scheduling refreshRunData when run ID changes in run overview when performing re-run ([6c48f2c](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/6c48f2c29e89cab264f9f154f03251b1ff44783b))
* **ui:** Reset run data on run ID route change, stopping data from being kept when changing runs (when using re-run action) ([d146224](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/d146224bf0af7dbd5ff38249524c648a9e8f2828))
* Update upload URL in API response for configuration version to provide full URL, rather than just path ([d874969](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/d87496928b75ebee1e57f523e346aaa7634a7536)), closes [#157](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/157)
