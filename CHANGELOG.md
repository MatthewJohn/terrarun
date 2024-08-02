# Changelog

## [0.62.1](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.62.0...v0.62.1) (2024-08-02)


### Bug Fixes

* Align tests to terraform-versions API ([9194339](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/91943395db54c5636d734cd6c9fe55374f029c48))
* Align UI to terraform-versions API changes ([f29f8f5](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/f29f8f575e65b1b1ed3686b664c8f178be7fe8f1))
* Attribute name fixed ([cdb78e9](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/cdb78e992d61386f9db11bd480914a6db7569b5e))
* Fix Terraform version entity attribute defaults ([4f3c38d](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/4f3c38de12b487a135f8f18dbeec781e63c16361))

# [0.62.0](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.61.0...v0.62.0) (2024-08-02)


### Bug Fixes

* Add new 'TEST' Job type for agents to avoid errors when connecting new agent ([71a6db6](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/71a6db617a58224d01b36f757c0e8a0d4f1a7e6a)), closes [#142](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/142)


### Features

* use first error status as response code ([e4484e1](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/e4484e19150e7579e903cfafafa0ba4f313df339))

# [0.61.0](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.60.2...v0.61.0) (2024-08-02)


### Bug Fixes

* Return early in job API endpoint from jobs that contain no specified tool version ([1725e23](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/1725e237a3ccfded25c103d89df42c53a355e930)), closes [#180](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/180)


### Features

* Add agent execution information to apply API response. ([178ca0f](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/178ca0f8db174e63037e2d0e000a9084aafe017a)), closes [#180](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/180)
* Add agent execution information to plan API response ([5c77f52](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/5c77f525ee5b1d59cafb7eb81e9b402b39029a77)), closes [#180](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/180)
* Set agent and execution mode to run/apply when being assigned to agent ([cf3ae43](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/cf3ae43f335e00d512f1b35dab893164fe8b4e95)), closes [#180](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/180)

## [0.60.2](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.60.1...v0.60.2) (2024-08-01)


### Bug Fixes

* official should be true when custom url is empty ([ecf67af](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/ecf67af9950cf6a83aa9aab748521c5e8da1d877))

## [0.60.1](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.60.0...v0.60.1) (2024-08-01)


### Bug Fixes

* Align the dev UI port to 3000 ([cc0be72](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/cc0be7284366ec90ef97c7d22df91ee7ee7f95ca))

# [0.60.0](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.59.2...v0.60.0) (2024-07-30)


### Bug Fixes

* Fix port for UI in local development ([486249c](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/486249cd9eecc66c9695b4040042d9b4e0c57fda)), closes [#170](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/170)
* Remove old agent pool project/workspace associations and replace with Project/workspace permissions ([44a130a](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/44a130a59e56a6eedbb315c9326cddf7df794b22)), closes [#170](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/170)
* Replace old "overrides" attribute of workspace/project with "settings-overwrites" to align with hashicorp API ([ce494b0](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/ce494b0d7ac90c40b9ec730a8aad4dd94ab9491d)), closes [#175](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/175) [#170](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/170)


### Features

* Add default agent pool attributes to environment and  project ([72ca825](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/72ca825e6b816e7ab4c71292120b983315725783)), closes [#170](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/170)
* Update job processor to take into account agent pool association at org, environment, project and workspace ([1c2d7f3](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/1c2d7f30e381b2ce6f15981d05981c34d939593e)), closes [#170](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/170)

## [0.59.2](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.59.1...v0.59.2) (2024-07-29)


### Bug Fixes

* Add missing status field from state-version API ([de9e11c](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/de9e11c592226f50b6db21dcc077af2f8bf9e4dd)), closes [#167](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/167) [#166](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/166)

## [0.59.1](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.59.0...v0.59.1) (2024-07-29)


### Bug Fixes

* Avoid returning 404 in current state outputs endpoint when current state has no outputs ([952ea3a](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/952ea3a79def708f8a1b3e3d49a20f89371919a3)), closes [#178](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/178)

# [0.59.0](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.58.1...v0.59.0) (2024-07-27)


### Bug Fixes

* Add additional depends and links to docker-compose ([21c37d3](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/21c37d30997971d457a52c9be43e334aa1f3b731)), closes [#174](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/174)
* Fix error when providing attributes other than name/email in organisation creation ([57ebbd5](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/57ebbd5ee9ec4898346c67558e3bfa17421a3fe7)), closes [#174](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/174)
* Fix length of example encryption key ([38b1fff](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/38b1fffa7e837ec1b84c62af7122e339604931d6)), closes [#174](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/174)
* Remove volume mounts for local code in docker-compose and add dev docker-compose with volume mounts ([2975cae](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/2975cae082d66c4ecbec7f6ef16184b1e776a3a7)), closes [#174](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/174)


### Features

* Add API endpoint to provide current state outputs for workspace. ([fcc02e4](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/fcc02e40e2166885a8c00249099dc79c1d404b18)), closes [#174](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/174)

## [0.58.1](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.58.0...v0.58.1) (2024-07-25)


### Bug Fixes

* Record confirmation user in job table and use when changing changes to confirmed ([2be9f04](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/2be9f040c63ee803a9ec7866e25dcd93871a6805)), closes [#168](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/168)

# [0.58.0](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.57.0...v0.58.0) (2024-07-25)


### Features

* Add API endpoint for showing agent pool ([1de0481](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/1de0481bc76c38cc0f9f46bbecf2d2efe8ade49d)), closes [#160](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/160)

# [0.57.0](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.56.1...v0.57.0) (2024-07-23)


### Bug Fixes

* Fix creating entity object from request data, passing attributes into attributes key, rather than kwargs ([61e1a12](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/61e1a1254ac99d796015d0e39f3241ef349644b5)), closes [#169](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/169)
* Fix error when instantiating error response in entities, due to missing base methods of error API view ([7864428](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/786442863d4b92a43b4484a9405a5465c52ef2a6)), closes [#159](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/159)
* Fix pointer in invalid type error in entities ([c66b034](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/c66b034ecf4c49280e3f53e48ac3d81fdca03f62)), closes [#159](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/159)
* Update property of agent pool organisation_scoped to match API attribute. ([09274fc](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/09274fce0a17c52cebcb09e037c1c36778963ce8)), closes [#159](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/159)


### Features

* Add default agent pool attribute to organisation model ([82e3381](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/82e33812d7e6af18e0ae8079cac7faa2c5aa078f)), closes [#159](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/159)
* Add default agent pool entity relationship to organisation ([54c4bd3](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/54c4bd3739100251eefd6938b68c456e2681a3c2)), closes [#159](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/159)
* Allow setting additional attributes to organisation on create/update API calls. ([36cb17c](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/36cb17c851a6f07280d8277587714e9dab559f1a)), closes [#159](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/159)
* Allow setting default agent pool of organisation through API ([0ce28bd](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/0ce28bd7101a8c738346b0f2ca21127ffa692194)), closes [#159](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/159)
* Convert organisation list API to use entity views using new ListView ([1761321](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/17613215a44aa5b85f0dcdd0805685553f5b58ad)), closes [#159](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/159)

## [0.56.1](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.56.0...v0.56.1) (2024-07-23)


### Bug Fixes

* Fix creating entity object from request data, passing attributes into attributes key, rather than kwargs ([134de2b](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/134de2b3f632d1b86595fd3cdd63e611735d0354)), closes [#169](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/169)

# [0.56.0](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.55.0...v0.56.0) (2024-07-22)


### Bug Fixes

* Disable setting agent job tokens to user, as we assume that job is available in most APIs ([8ead2fb](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/8ead2fb0186f6f34d6da6ad7be740c664bc3a8d0)), closes [#162](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/162)


### Features

* Add created_by and created_at fields of state version and add to API response ([96a7d47](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/96a7d47080dd7e2cf37f69a67fa2535e926e437f)), closes [#162](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/162)

# [0.55.0](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/compare/v0.54.2...v0.55.0) (2024-07-22)


### Bug Fixes

* Set UNDEFINED and ATTRIBUTED_REQUIRED as instances of object to ensure that they are correctly identitied ([265a69b](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/265a69b7719a1a2858372e8548b3c3ce9365d3ce)), closes [#150](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/150)


### Features

* Add default execution mode attribute to organisation. ([5055090](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/50550901c84c26c7a5a3c6be2b19aeb15eefd131)), closes [#150](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/150)
* Add selection of default execution mode to organisation settings in UI. ([65f8fc6](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/65f8fc6714a4d737cb0c0131f87c4d71dae46f67)), closes [#150](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/150)
* Allow setting project execution mode to "inherit" ([bbe12c8](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/commit/bbe12c8ca77d2b96527e1bbc2c079620918ed36f)), closes [#150](https://gitlab.dockstudios.co.uk/pub/terra/terrarun/issues/150)

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
