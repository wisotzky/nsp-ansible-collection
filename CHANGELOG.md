# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2026-02-16

### Added

- Initial release of Nokia NSP Ansible Collection
- **Modules:**
  - `nokia.nsp.rpc` - Execute global YANG RPC operations on Nokia NSP
  - `nokia.nsp.action` - Execute YANG actions on RESTCONF resources
  - `nokia.nsp.version` - Retrieve Nokia NSP system version information
  - `nokia.nsp.rest` - Execute REST API calls against Nokia NSP
  - `nokia.nsp.upload` - Upload files to Nokia NSP
  - `nokia.nsp.download` - Download files from Nokia NSP
  - `nokia.nsp.wfm` - Manage Nokia NSP Workflow Manager workflows
- **HTTP API Plugin:**
  - `nokia.nsp.nsp` - HTTP API plugin with NSP authentication
- **Features:**
  - Client authentication
  - Automatic token lifecycle management
  - Bearer token injection in request headers
  - Comprehensive error handling
  - Full type hints and docstrings
- **Documentation:**
  - Complete module reference with examples
  - mkdocs-based documentation site
  **Testing:**
  - Basic testing with Ansible 2.14 and Python 3.11
  - Security scanning
- **Development:**
  - Separate requirements files (production vs dev)
  - Code quality tools (flake8, pylint, black)
  - Documentation auto-generation from docstrings
  - Runtime requirements enforcement with clear error messages
  - Pylint compliance (10.00/10)


## Release Information

**Current Version:** 0.0.1  
**Release Date:** 2026-02-16  
**Status:** Work in Progress  
**Target:** Moving to github.com/nokia organization

[0.0.1]: https://github.com/wisotzky/nsp-ansible-collection/releases/tag/v0.0.1
