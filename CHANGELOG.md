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
