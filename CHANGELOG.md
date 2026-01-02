# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 2026-01-03
### Added
- **🏆 M+ Support:** Support for Mythic+ (Retail) and MoP-style Challenge Modes.
- **🔑 M+ Key Level Detection:** Filenames now automatically extract and include the specific key level (e.g., `+15`) from the combat log.
- **📍 Nested Boss Chapters:** While recording a dungeon run, the script now injects sub-chapters for every individual boss pull and result.
- **🛡️ Stability Fixes:** Implemented a file-handle retry loop to prevent `PermissionError` during muxing/renaming.
- **💻 Refined UI:** Updated the launcher with expansion detection (RETAIL vs CLASSIC) and improved folder path troubleshooting.
- **🌟 Universal Expansion Support:** Updated core regex to ensure compatibility with **Retail**, **Classic (Cata/MoP)**, and **TBC Anniversary** servers.
- **🌍 Global Name Handling:** Support for all global naming formats (`Name-Realm`) across all regions.

## [1.2.0] - 2026-01-02
### Added
- **🎨 ANSI Color Coding:** The console now uses colors for better readability (Green = Success, Red = Death, Cyan = Recording).
- **🖥️ Terminal UI Improvements:** Cleaned up the log output to be more professional and scannable.
- **✨ README Preview:** Added a console output example to the documentation.

## [1.0.0] - 2025-12-28
### Added
- **🚀 Initial Stable Release:** Official launch featuring auto-recording, boss-based renaming, and basic death chaptering.