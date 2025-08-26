# Change Log

## [Unreleased]

### Fixed
- **Critical Test Coverage**: Restored `tests/__init__.py` which was accidentally deleted, breaking test discovery and removing all test coverage
- **Input Validation**: Added comprehensive validation for month format inputs in `parse_month_range()` function
  - Validates YYYY-MM format with regex pattern matching
  - Provides clear error messages for invalid formats
  - Handles empty/null inputs gracefully
  - Validates month ranges (start cannot be after end)
- **Network Error Handling**: Enhanced network operation error handling in `upload_to_anycost()` function
  - Added 30-second timeout for API requests
  - Specific handling for timeout, connection, and HTTP errors
  - Detailed error messages with request context
  - JSON error response parsing for API errors
  - Graceful handling of unexpected errors

### Added
- **AnyCost Stream API Compliance**: Updated `upload_to_anycost()` function to include required `month` parameter in ISO 8601 format (e.g., "2024-08")
- **Batch Processing**: Added support for uploading data to multiple months in a single session
  - Single month: `2024-08`
  - Month range: `2024-08:2024-10` (uploads to Aug, Sep, Oct)  
  - Comma-separated: `2024-08,2024-09,2024-11`
  - Progress tracking and error resilience for batch uploads
- **Operation Type Support**: Added support for operation types when uploading to AnyCost Stream:
  - `replace_drop` (default): Replace all existing data for the month
  - `replace_hourly`: Replace data with overlapping hours  
  - `sum`: Append data to existing records
- **Rich Error Handling**: Comprehensive error handling with helpful messages
  - Input validation with retry logic (3 attempts)
  - Month format validation with specific error messages
  - File processing errors with row-by-row reporting
  - Network timeout and connection error handling
  - API response validation and error reporting
- **Interactive Prompts**: Added user prompts for processing mode, month selection, and operation type during upload
- **Comprehensive Test Suite**: Added unit tests covering all functions with 20 test cases
  - Tests for CSV processing, data transformation, and API upload functionality
  - Tests for month range parsing and batch processing functionality
  - Mocked external dependencies for reliable testing
  - Located in `tests/` directory with pytest framework
- **Developer Experience**: Enhanced documentation and code comments for easy customization
  - Step-by-step customization guide for different cloud providers
  - Field mapping examples for AWS, Azure, and GCP
  - Troubleshooting section with common issues and solutions
  - Inline code comments marking customization points

### Changed  
- Enhanced function documentation to explain all required and optional parameters for AnyCost Stream uploads
- Updated file header comments to document month and operation requirements  
- Removed beta warning from README as AnyCost Stream is now generally available
- Improved README structure with Quick Start guide and detailed customization instructions

### Technical Details
- JSON payload now includes `month`, `operation`, and `data` fields as per AnyCost Stream API specification
- Added `parse_month_range()` function to handle different month input formats
- Batch processing makes sequential API calls with error handling and progress tracking
- Maintains backward compatibility while adding new required functionality
- All 20 tests pass successfully with proper mocking of external dependencies

---

## Resources for generating a changelog:

[skywinder/Github-Changelog-Generator](https://github.com/skywinder/Github-Changelog-Generator) - generates a full changelog that overwrites the existing CHANGELOG.md. 

[hzalaz/wt-oss-milestone-changelog](https://github.com/hzalaz/wt-oss-milestone-changelog) - generates a snippet of Markdown that can be added to a CHANGELOG.md.

[conventional-changelog/conventional-changelog](https://github.com/conventional-changelog/conventional-changelog/tree/master/packages/conventional-changelog-cli) - generates a full changelog based on commit history with the option to append to an existing changelog.