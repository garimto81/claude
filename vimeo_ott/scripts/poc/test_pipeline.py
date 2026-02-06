"""
WSOPTV OTT Pipeline POC Test.

Tests the complete NAS → S3 → Vimeo workflow with sample files.

Usage:
    python test_pipeline.py --test-s3       # Test S3 only
    python test_pipeline.py --test-vimeo    # Test Vimeo only
    python test_pipeline.py --test-full     # Test full pipeline
    python test_pipeline.py --dry-run       # Show plan without executing
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add parent paths (resolve() ensures absolute paths on Windows)
_SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR / "vimeo"))

from aws.s3_client import S3Client
from auth import get_client as get_vimeo_client


@dataclass
class TestFile:
    """Represents a test file."""
    name: str
    source_path: str
    s3_key: str
    size_bytes: int = 0
    s3_uploaded: bool = False
    vimeo_uri: str | None = None
    status: str = "pending"


@dataclass
class TestResult:
    """POC test results."""
    test_name: str
    success: bool
    duration_seconds: float
    details: dict


class PipelinePOC:
    """POC test runner for WSOPTV pipeline."""

    # POC test files (WSOP Classic 1973-1975)
    TEST_FILES = [
        "Z:\\GGPNAs\\ARCHIVE\\WSOP\\WSOP Classic (1973 - 2002)\\WSOP 1973\\WSOP - 1973.avi",
        "Z:\\GGPNAs\\ARCHIVE\\WSOP\\WSOP Classic (1973 - 2002)\\WSOP 1974\\WSOP - 1974.avi",
        "Z:\\GGPNAs\\ARCHIVE\\WSOP\\WSOP Classic (1973 - 2002)\\WSOP 1975\\WSOP - 1975.avi",
    ]

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.results: List[TestResult] = []
        self.test_files: List[TestFile] = []

        # Results file
        self.results_path = Path(__file__).parent.parent.parent / "docs" / "03-analysis"
        self.results_path.mkdir(parents=True, exist_ok=True)

    def discover_test_files(self) -> List[TestFile]:
        """Discover available test files."""
        print("\n🔍 Discovering test files...")

        test_files = []
        for path in self.TEST_FILES:
            p = Path(path)
            if p.exists():
                # Generate S3 key from path
                # Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic...\1973\file.avi
                # → raw/wsop-classic/1973/file.avi
                parts = p.parts
                year = "unknown"
                for part in parts:
                    if part.isdigit() and 1970 <= int(part) <= 2030:
                        year = part
                        break
                    elif "WSOP" in part and any(c.isdigit() for c in part):
                        # Extract year from "WSOP 1973"
                        year = "".join(c for c in part if c.isdigit())
                        break

                s3_key = f"raw/wsop-classic/{year}/{p.name.lower().replace(' ', '-')}"

                test_files.append(TestFile(
                    name=p.name,
                    source_path=str(p),
                    s3_key=s3_key,
                    size_bytes=p.stat().st_size,
                ))
                print(f"   ✅ Found: {p.name} ({p.stat().st_size / 1024 / 1024:.2f} MB)")
            else:
                print(f"   ⚠️ Not found: {path}")

        if not test_files:
            print("\n❌ No test files found. Using sample test file...")
            # Create a small test file for POC
            sample_path = Path(__file__).parent / "sample_test.txt"
            sample_path.write_text("WSOPTV POC Test File\n" * 1000)
            test_files.append(TestFile(
                name="sample_test.txt",
                source_path=str(sample_path),
                s3_key="test/poc/sample_test.txt",
                size_bytes=sample_path.stat().st_size,
            ))
            print(f"   ✅ Created sample: {sample_path}")

        self.test_files = test_files
        return test_files

    def test_s3_connection(self) -> TestResult:
        """Test S3 connection and credentials."""
        print("\n🧪 Test 1: S3 Connection")
        print("-" * 40)

        start = time.time()

        if self.dry_run:
            print("   [DRY RUN] Would check S3 credentials and bucket")
            return TestResult(
                test_name="s3_connection",
                success=True,
                duration_seconds=0,
                details={"dry_run": True},
            )

        try:
            client = S3Client()

            # Check credentials
            creds_valid = client.check_credentials()
            print(f"   Credentials: {'✅ Valid' if creds_valid else '❌ Invalid'}")

            # Check bucket
            bucket_exists = client.bucket_exists()
            print(f"   Bucket: {'✅ Exists' if bucket_exists else '⚠️ Not found'}")

            if not bucket_exists:
                print("   Creating bucket...")
                client.create_bucket()

            duration = time.time() - start
            result = TestResult(
                test_name="s3_connection",
                success=creds_valid,
                duration_seconds=duration,
                details={
                    "credentials_valid": creds_valid,
                    "bucket_exists": bucket_exists,
                },
            )
            self.results.append(result)
            return result

        except Exception as e:
            duration = time.time() - start
            result = TestResult(
                test_name="s3_connection",
                success=False,
                duration_seconds=duration,
                details={"error": str(e)},
            )
            self.results.append(result)
            return result

    def test_s3_upload(self) -> TestResult:
        """Test S3 file upload."""
        print("\n🧪 Test 2: S3 Upload")
        print("-" * 40)

        start = time.time()

        if not self.test_files:
            self.discover_test_files()

        if self.dry_run:
            print(f"   [DRY RUN] Would upload {len(self.test_files)} files to S3")
            for tf in self.test_files:
                print(f"      {tf.name} → s3://wsoptv-archive/{tf.s3_key}")
            return TestResult(
                test_name="s3_upload",
                success=True,
                duration_seconds=0,
                details={"dry_run": True, "file_count": len(self.test_files)},
            )

        try:
            client = S3Client()
            uploaded = []
            failed = []

            for tf in self.test_files:
                print(f"\n   Uploading: {tf.name}")
                try:
                    # Check for duplicate
                    if client.check_duplicate(tf.source_path, tf.s3_key):
                        print(f"   ⏭️ Skipped (already exists): {tf.s3_key}")
                        tf.s3_uploaded = True
                        tf.status = "s3_uploaded"
                        uploaded.append(tf.name)
                        continue

                    # Upload
                    client.upload_file(tf.source_path, tf.s3_key)
                    tf.s3_uploaded = True
                    tf.status = "s3_uploaded"
                    uploaded.append(tf.name)

                except Exception as e:
                    print(f"   ❌ Failed: {e}")
                    tf.status = "failed"
                    failed.append({"name": tf.name, "error": str(e)})

            duration = time.time() - start
            success = len(failed) == 0

            result = TestResult(
                test_name="s3_upload",
                success=success,
                duration_seconds=duration,
                details={
                    "uploaded": uploaded,
                    "failed": failed,
                    "total": len(self.test_files),
                },
            )
            self.results.append(result)
            return result

        except Exception as e:
            duration = time.time() - start
            result = TestResult(
                test_name="s3_upload",
                success=False,
                duration_seconds=duration,
                details={"error": str(e)},
            )
            self.results.append(result)
            return result

    def test_vimeo_connection(self) -> TestResult:
        """Test Vimeo connection and authentication."""
        print("\n🧪 Test 3: Vimeo Connection")
        print("-" * 40)

        start = time.time()

        if self.dry_run:
            print("   [DRY RUN] Would check Vimeo OAuth token")
            return TestResult(
                test_name="vimeo_connection",
                success=True,
                duration_seconds=0,
                details={"dry_run": True},
            )

        try:
            client = get_vimeo_client()

            # Test API call
            response = client.get("/me")
            if response.status_code == 200:
                user = response.json()
                print(f"   ✅ Authenticated as: {user.get('name', 'Unknown')}")
                print(f"   Account: {user.get('account', 'Unknown')}")

                # Check quota
                quota = user.get("upload_quota", {}).get("space", {})
                used_gb = quota.get("used", 0) / 1024 / 1024 / 1024
                free_gb = quota.get("free", 0) / 1024 / 1024 / 1024
                print(f"   Storage: {used_gb:.2f} GB used, {free_gb:.2f} GB free")

                duration = time.time() - start
                result = TestResult(
                    test_name="vimeo_connection",
                    success=True,
                    duration_seconds=duration,
                    details={
                        "user": user.get("name"),
                        "account": user.get("account"),
                        "storage_used_gb": used_gb,
                        "storage_free_gb": free_gb,
                    },
                )
            else:
                print(f"   ❌ API Error: {response.status_code}")
                duration = time.time() - start
                result = TestResult(
                    test_name="vimeo_connection",
                    success=False,
                    duration_seconds=duration,
                    details={"error": f"API returned {response.status_code}"},
                )

            self.results.append(result)
            return result

        except Exception as e:
            duration = time.time() - start
            result = TestResult(
                test_name="vimeo_connection",
                success=False,
                duration_seconds=duration,
                details={"error": str(e)},
            )
            self.results.append(result)
            return result

    def test_vimeo_upload(self) -> TestResult:
        """Test Vimeo file upload from S3."""
        print("\n🧪 Test 4: Vimeo Upload")
        print("-" * 40)

        start = time.time()

        # Only upload files that are already in S3
        s3_files = [tf for tf in self.test_files if tf.s3_uploaded]

        if not s3_files:
            print("   ⚠️ No files in S3 to upload to Vimeo")
            return TestResult(
                test_name="vimeo_upload",
                success=False,
                duration_seconds=0,
                details={"error": "No S3 files available"},
            )

        if self.dry_run:
            print(f"   [DRY RUN] Would upload {len(s3_files)} files to Vimeo")
            for tf in s3_files:
                print(f"      {tf.name} → Vimeo")
            return TestResult(
                test_name="vimeo_upload",
                success=True,
                duration_seconds=0,
                details={"dry_run": True, "file_count": len(s3_files)},
            )

        try:
            vimeo_client = get_vimeo_client()
            s3_client = S3Client()
            uploaded = []
            failed = []

            for tf in s3_files[:1]:  # Only upload first file for POC
                print(f"\n   Uploading to Vimeo: {tf.name}")

                try:
                    # Generate presigned URL
                    presigned_url = s3_client.generate_presigned_url(tf.s3_key)

                    # For POC, we upload from local path
                    # In production, we'd use presigned URL or download first
                    print(f"   Uploading from: {tf.source_path}")

                    uri = vimeo_client.upload(
                        tf.source_path,
                        data={
                            "name": f"[POC] {tf.name}",
                            "description": "WSOPTV POC Test Upload",
                            "privacy": {"view": "unlisted"},
                        },
                    )

                    tf.vimeo_uri = uri
                    tf.status = "transcoding"
                    uploaded.append({"name": tf.name, "uri": uri})
                    print(f"   ✅ Uploaded: {uri}")

                except Exception as e:
                    print(f"   ❌ Failed: {e}")
                    tf.status = "failed"
                    failed.append({"name": tf.name, "error": str(e)})

            duration = time.time() - start
            success = len(failed) == 0 and len(uploaded) > 0

            result = TestResult(
                test_name="vimeo_upload",
                success=success,
                duration_seconds=duration,
                details={
                    "uploaded": uploaded,
                    "failed": failed,
                    "total": len(s3_files),
                },
            )
            self.results.append(result)
            return result

        except Exception as e:
            duration = time.time() - start
            result = TestResult(
                test_name="vimeo_upload",
                success=False,
                duration_seconds=duration,
                details={"error": str(e)},
            )
            self.results.append(result)
            return result

    def generate_report(self) -> str:
        """Generate POC test report."""
        print("\n📊 Generating Report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "test_files": [asdict(tf) for tf in self.test_files],
            "results": [asdict(r) for r in self.results],
            "summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
                "total_duration": sum(r.duration_seconds for r in self.results),
            },
        }

        # Save JSON
        json_path = self.results_path / f"poc-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Saved: {json_path}")

        # Generate markdown report
        md_content = f"""# WSOPTV POC Test Results

| 항목 | 값 |
|------|---|
| **실행 시간** | {report['timestamp']} |
| **Dry Run** | {report['dry_run']} |
| **총 테스트** | {report['summary']['total_tests']} |
| **성공** | {report['summary']['passed']} |
| **실패** | {report['summary']['failed']} |
| **총 소요 시간** | {report['summary']['total_duration']:.2f}초 |

---

## 테스트 결과

| 테스트 | 결과 | 소요 시간 |
|--------|:----:|----------:|
"""
        for r in self.results:
            status = "✅ 성공" if r.success else "❌ 실패"
            md_content += f"| {r.test_name} | {status} | {r.duration_seconds:.2f}s |\n"

        md_content += f"""
---

## 테스트 파일

| 파일명 | 크기 | S3 | Vimeo | 상태 |
|--------|-----:|:--:|:-----:|------|
"""
        for tf in self.test_files:
            size_mb = tf.size_bytes / 1024 / 1024
            s3_status = "✅" if tf.s3_uploaded else "❌"
            vimeo_status = "✅" if tf.vimeo_uri else "❌"
            md_content += f"| {tf.name} | {size_mb:.2f} MB | {s3_status} | {vimeo_status} | {tf.status} |\n"

        md_content += f"""
---

## 상세 결과

```json
{json.dumps(report, indent=2, ensure_ascii=False)}
```
"""

        md_path = self.results_path / "poc-results.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"   ✅ Saved: {md_path}")

        return str(md_path)

    def run_all(self) -> None:
        """Run all POC tests."""
        print("=" * 60)
        print("  WSOPTV OTT Pipeline POC Test")
        print("=" * 60)

        if self.dry_run:
            print("\n⚠️ DRY RUN MODE - No actual operations will be performed\n")

        # Discover files
        self.discover_test_files()

        # Run tests
        self.test_s3_connection()
        self.test_s3_upload()
        self.test_vimeo_connection()
        self.test_vimeo_upload()

        # Generate report
        self.generate_report()

        # Summary
        print("\n" + "=" * 60)
        print("  Summary")
        print("=" * 60)
        passed = sum(1 for r in self.results if r.success)
        total = len(self.results)
        print(f"\n   결과: {passed}/{total} 테스트 통과")

        if passed == total:
            print("   ✅ POC 테스트 성공!")
        else:
            print("   ❌ 일부 테스트 실패. 상세 결과를 확인하세요.")


def main():
    parser = argparse.ArgumentParser(description="WSOPTV POC Test")
    parser.add_argument("--test-s3", action="store_true", help="Test S3 only")
    parser.add_argument("--test-vimeo", action="store_true", help="Test Vimeo only")
    parser.add_argument("--test-full", action="store_true", help="Run full pipeline test")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")

    args = parser.parse_args()

    poc = PipelinePOC(dry_run=args.dry_run)

    if args.test_s3:
        poc.discover_test_files()
        poc.test_s3_connection()
        poc.test_s3_upload()
        poc.generate_report()
    elif args.test_vimeo:
        poc.discover_test_files()
        poc.test_vimeo_connection()
        poc.test_vimeo_upload()
        poc.generate_report()
    elif args.test_full or not (args.test_s3 or args.test_vimeo):
        poc.run_all()


if __name__ == "__main__":
    main()
