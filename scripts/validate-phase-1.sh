#!/bin/bash
# Bash wrapper for validate-phase-1.ps1
# Calls PowerShell script on Windows

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v powershell &> /dev/null; then
    powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/validate-phase-1.ps1" "$@"
elif command -v pwsh &> /dev/null; then
    pwsh -File "$SCRIPT_DIR/validate-phase-1.ps1" "$@"
else
    echo "Error: PowerShell is not installed"
    exit 1
fi
