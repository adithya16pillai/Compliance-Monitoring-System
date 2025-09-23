#!/usr/bin/env python3
"""
Security Scanner for Compliance Monitoring System
Checks for sensitive files and data before git commits
"""

import os
import re
import sys
import glob
from pathlib import Path

# Sensitive file patterns to check
SENSITIVE_PATTERNS = [
    r'\.env$',
    r'\.env\.',
    r'secrets\.',
    r'credentials\.',
    r'api_keys\.',
    r'\.key$',
    r'\.pem$',
    r'\.crt$',
    r'\.p12$',
    r'\.pfx$',
    r'\.db$',
    r'\.sqlite',
    r'service-account.*\.json$',
]

# Sensitive content patterns
SENSITIVE_CONTENT_PATTERNS = [
    r'sk-[a-zA-Z0-9]{48}',  # OpenAI API keys
    r'sk-ant-[a-zA-Z0-9\-_]{95}',  # Anthropic API keys
    r'AKIA[0-9A-Z]{16}',  # AWS Access Key ID
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',  # UUIDs (potential secrets)
    r'password\s*=\s*["\'][^"\']+["\']',  # Hardcoded passwords
    r'secret\s*=\s*["\'][^"\']+["\']',  # Hardcoded secrets
    r'token\s*=\s*["\'][^"\']+["\']',  # Hardcoded tokens
]

def check_sensitive_files():
    """Check for sensitive files in the repository"""
    print("🔍 Scanning for sensitive files...")
    sensitive_files = []
    
    for pattern in SENSITIVE_PATTERNS:
        files = glob.glob(f"**/*", recursive=True)
        for file in files:
            if re.search(pattern, file, re.IGNORECASE):
                if os.path.isfile(file):
                    sensitive_files.append(file)
    
    return sensitive_files

def check_sensitive_content():
    """Check for sensitive content in code files"""
    print("🔍 Scanning for sensitive content in code...")
    violations = []
    
    code_extensions = ['.py', '.js', '.ts', '.yaml', '.yml', '.json', '.md', '.txt']
    
    for ext in code_extensions:
        files = glob.glob(f"**/*{ext}", recursive=True)
        for file in files:
            # Skip files that should be ignored
            if any(ignore in file for ignore in ['.git/', '__pycache__/', '.venv/', 'node_modules/']):
                continue
                
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in SENSITIVE_CONTENT_PATTERNS:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append({
                            'file': file,
                            'line': line_num,
                            'pattern': pattern,
                            'match': match.group()
                        })
            except Exception as e:
                print(f"⚠️  Warning: Could not read {file}: {e}")
    
    return violations

def check_git_status():
    """Check git status for staged sensitive files"""
    print("🔍 Checking git status...")
    
    try:
        import subprocess
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        staged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        sensitive_staged = []
        for file in staged_files:
            for pattern in SENSITIVE_PATTERNS:
                if re.search(pattern, file, re.IGNORECASE):
                    sensitive_staged.append(file)
        
        return sensitive_staged
    except Exception as e:
        print(f"⚠️  Warning: Could not check git status: {e}")
        return []

def main():
    """Main security scan function"""
    print("🛡️  Compliance Monitoring System - Security Scanner")
    print("=" * 60)
    
    # Check for sensitive files
    sensitive_files = check_sensitive_files()
    if sensitive_files:
        print("❌ SENSITIVE FILES DETECTED:")
        for file in sensitive_files:
            print(f"   📄 {file}")
        print()
    
    # Check for sensitive content
    violations = check_sensitive_content()
    if violations:
        print("❌ SENSITIVE CONTENT DETECTED:")
        for violation in violations:
            print(f"   📄 {violation['file']}:{violation['line']} - {violation['match']}")
        print()
    
    # Check git staging area
    staged_sensitive = check_git_status()
    if staged_sensitive:
        print("❌ SENSITIVE FILES STAGED FOR COMMIT:")
        for file in staged_sensitive:
            print(f"   📄 {file}")
        print()
        print("🚨 Run: git reset HEAD <file> to unstage")
        print()
    
    # Summary
    total_issues = len(sensitive_files) + len(violations) + len(staged_sensitive)
    
    if total_issues == 0:
        print("✅ Security scan passed! No sensitive data detected.")
        return 0
    else:
        print(f"❌ Security scan failed! {total_issues} issues detected.")
        print()
        print("📋 Next steps:")
        print("1. Review the files listed above")
        print("2. Move sensitive data to .env file")
        print("3. Add files to .gitignore if needed")
        print("4. Use git reset to unstage sensitive files")
        print("5. Run this scan again")
        return 1

if __name__ == "__main__":
    sys.exit(main())