#!/usr/bin/env python3
"""
package_submission.py
Creates the official code.zip submission artifact for HackerRank Orchestrate.
Contains strictly the code package and usage report without dataset files or caches.
"""

import os
import zipfile

def package_submission():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(repo_root, 'code.zip')
    
    files_to_pack = [
        ('README.md', os.path.join(repo_root, 'code', 'README.md')),
        ('code/README.md', os.path.join(repo_root, 'code', 'README.md')),
        ('code/main.py', os.path.join(repo_root, 'code', 'main.py')),
        ('code/requirements.txt', os.path.join(repo_root, 'code', 'requirements.txt')),
        ('code/test_safe_amount.py', os.path.join(repo_root, 'code', 'test_safe_amount.py')),
        ('code/.env.example', os.path.join(repo_root, 'code', '.env.example')),
        ('evaluation/usage_report.md', os.path.join(repo_root, 'evaluation', 'usage_report.md')),
    ]
    
    print(f"Creating submission package at: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for arcname, fpath in files_to_pack:
            if os.path.exists(fpath):
                z.write(fpath, arcname)
                print(f"  + Added: {arcname} ({os.path.getsize(fpath):,} bytes)")
            else:
                print(f"  ! Error: Required file missing: {fpath}")
                raise FileNotFoundError(f"Missing submission artifact: {fpath}")

    print(f"\nVerification of {zip_path}:")
    with zipfile.ZipFile(zip_path, 'r') as z:
        for info in z.infolist():
            print(f"  - {info.filename:32s} {info.file_size:6d} bytes")
    print("\nSubmission archive successfully prepared!")

if __name__ == '__main__':
    package_submission()
