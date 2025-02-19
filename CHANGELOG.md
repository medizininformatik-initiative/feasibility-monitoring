# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [UNRELEASED] - yyyy-mm-dd

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.2.7] - 2025-02-19

### Added

- Make ping task configurable ([#51](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/51))

### Changed

- Changed order or report queries - medication query last ([#49](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/49))

## [0.2.6] - 2025-02-05

### Added

- Added MedicationStatement and MedicationRequest to Medication query ([#46](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/46))


## [0.2.5] - 2024-12-05

### Changed

- Remove 119376003 - tissue specimen - as too many children ([#43](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/43))

## [0.2.4] - 2024-12-05

### Added

- Updated site idents in config and added activity definition translations


## [0.2.3] - 2024-12-05

### Fixed

### Added

- Added new loinc codes to lab query ([#37](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/37))

## [0.2.2] - 2024-09-17

### Fixed

### Added

- Added new loinc code ([#28](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/28))
- Added new ATC and changed specimen code ([#26](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/26))
- Added ActivityDefinition query ([#25](https://github.com/medizininformatik-initiative/feasibility-monitoring/pull/25))
- Added collection of kds report overview

## [0.2.1] - 2024-02-16

### Fixed
- History test table does not show last 14 days ([#19](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/19))

## [0.2.0] - 2024-01-23

### Added
- Add logging ([#7](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/7))
- Generate Ping Report Summary ([#10](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/10))
- Add additional Specimen queries ([#15](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/15))
- Add additional Laboratory Values ([#17](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/17))

### Changed
- History Table - display order date columns from newest to oldest ([#11](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/11))
- Sort rows for all tables alphabetically by sitename ([#12](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/12))

### Fixed
- Set docker image to release ([#6](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/6))
- Include all sites that answer into report ([#8](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/8))
- Site Url -> Site Identifier in table ([#9](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/9))
- Adding new site breaks history table ([#13](https://github.com/medizininformatik-initiative/feasibility-monitoring/issues/13))

## [0.1.0] - 2024-01-23

### Added
- Add `Changelog.md`
- Add `Development.md`
- Add `.env.default`
- Add github workflow to automate the Docker image build process
- Add history table to display results over time
- Add shell script to execute the monitoring without docker for easier testing during development
    
### Changed
- Update Readme
- Rename and move files for better file structure
- Extend feasibility test to evaluate multilpe modules
- Extend feasibility table to display additional summary fields
- Make Confluence page content and DSF sites configurable
