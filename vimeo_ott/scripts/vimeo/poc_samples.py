"""
POC Sample Files Configuration.

Defines the 10 sample files for Vimeo Direct Upload POC.
Uses smaller MP4 files (*-nobug.mp4) for faster testing.
"""

from pathlib import Path

# NAS base path
NAS_BASE = Path(r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)")

# POC Sample files (10 files, ~35 GB total)
POC_SAMPLES = [
    NAS_BASE / "WSOP 1973" / "WSOP - 1973.avi",           # 728 MB - smallest file
    NAS_BASE / "WSOP 1978" / "wsop-1978-me-nobug.mp4",    # 1.5 GB
    NAS_BASE / "WSOP 1983" / "wsop-1983-me-nobug.mp4",    # 3.3 GB
    NAS_BASE / "WSOP 1989" / "wsop-1989-me_nobug.mp4",    # 1.8 GB
    NAS_BASE / "WSOP 1992" / "wsop-1992-me-nobug.mp4",    # 3.5 GB
    NAS_BASE / "WSOP 1994" / "wsop-1994-me-nobug.mp4",    # 3.5 GB
    NAS_BASE / "WSOP 1995" / "wsop-1995-me-nobug.mp4",    # 4.0 GB
    NAS_BASE / "WSOP 1998" / "wsop-1998-me-nobug.mp4",    # 4.2 GB
    NAS_BASE / "WSOP 2000" / "wsop-2000-me-nobug.mp4",    # 5.5 GB
    NAS_BASE / "WSOP 2001" / "wsop-2001-me-nobug.mp4",    # 5.5 GB
]


def get_sample_files() -> list[Path]:
    """Get list of POC sample files that exist."""
    return [p for p in POC_SAMPLES if p.exists()]


def validate_samples() -> dict:
    """Validate sample files and return summary."""
    results = {
        "total": len(POC_SAMPLES),
        "exists": 0,
        "missing": [],
        "total_size_gb": 0,
        "files": [],
    }

    for path in POC_SAMPLES:
        if path.exists():
            results["exists"] += 1
            size_gb = path.stat().st_size / 1024 / 1024 / 1024
            results["total_size_gb"] += size_gb
            results["files"].append({
                "path": str(path),
                "name": path.name,
                "size_gb": round(size_gb, 2),
            })
        else:
            results["missing"].append(str(path))

    return results


if __name__ == "__main__":

    print("POC Sample Files Validation")
    print("=" * 60)

    results = validate_samples()

    print(f"\nTotal files: {results['total']}")
    print(f"Exists: {results['exists']}")
    print(f"Total size: {results['total_size_gb']:.2f} GB")

    if results["files"]:
        print("\nFiles:")
        for f in results["files"]:
            print(f"  - {f['name']} ({f['size_gb']} GB)")

    if results["missing"]:
        print("\nMissing:")
        for m in results["missing"]:
            print(f"  - {m}")

    print("=" * 60)
