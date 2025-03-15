#!/usr/bin/env python3
"""
Script to complete the chat template migration process.

This script:
1. Ensures all views use the unified templates
2. Verifies no dead references to old templates remain
3. Documents the final state of the migration
"""

import os
import sys
import re
from pathlib import Path

# Templates that have been deleted and should not be referenced
DELETED_TEMPLATES = [
    "interaction/direct_chat.html",
    "interaction/direct_chat_enhanced.html",
    "interaction/direct_chat_fixed.html",
    "interaction/direct_chat_fixed_alignment.html",
    "interaction/direct_chat_minimal.html",
    "interaction/direct_chat_new.html",
    "interaction/direct_chat_no_debug.html",
]

# Directories to search for potential references
SEARCH_DIRS = [
    "interaction",
    "core",
    "catalog",
]

def find_template_references():
    """
    Find any references to deleted templates in the codebase.
    Returns a dictionary mapping template paths to files that reference them.
    """
    references = {template: [] for template in DELETED_TEMPLATES}
    
    # Search all Python and HTML files in the specified directories
    for directory in SEARCH_DIRS:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.html')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            for template in DELETED_TEMPLATES:
                                # Replace slashes with platform-appropriate separator for matching
                                search_template = template.replace('/', os.sep)
                                if search_template in content:
                                    references[template].append(file_path)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    return references

def update_template_references(references):
    """
    Update any references to the old templates to use the new unified templates.
    """
    # Mapping from old templates to new templates
    template_mapping = {
        "interaction/direct_chat.html": "interaction/unified/direct_chat.html",
        "interaction/direct_chat_enhanced.html": "interaction/unified/enhanced_chat.html",
        "interaction/direct_chat_minimal.html": "interaction/unified/minimal_debug_chat.html",
        "interaction/direct_chat_fixed.html": "interaction/unified/direct_chat.html",
        "interaction/direct_chat_fixed_alignment.html": "interaction/unified/direct_chat.html",
        "interaction/direct_chat_new.html": "interaction/unified/modern_chat.html",
        "interaction/direct_chat_no_debug.html": "interaction/unified/direct_chat.html",
    }
    
    files_updated = []
    
    # Update each file that references an old template
    for template, files in references.items():
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace the old template with the new one
                new_template = template_mapping.get(template, "interaction/unified/direct_chat.html")
                updated_content = content.replace(template, new_template)
                
                # Only write if changes were made
                if updated_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    files_updated.append(file_path)
                    print(f"Updated {file_path}: replaced {template} with {new_template}")
            except Exception as e:
                print(f"Error updating {file_path}: {e}")
    
    return files_updated

def check_view_defaults():
    """
    Check if all views have been updated to use the new unified templates as defaults.
    """
    view_file = "interaction/views/chat.py"
    issues = []
    
    try:
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for function definitions with template parameters
            pattern = r"def\s+(\w+)\s*\([^)]*template\s*=\s*['\"]([^'\"]+)['\"]"
            matches = re.findall(pattern, content)
            
            for func_name, template in matches:
                if not template.startswith('interaction/unified/'):
                    issues.append(f"Function {func_name} uses non-unified template default: {template}")
    except Exception as e:
        print(f"Error checking view defaults: {e}")
    
    return issues

def generate_report(references, files_updated, issues):
    """
    Generate a report of the migration status.
    """
    report = []
    report.append("# Chat Template Migration Status Report")
    report.append("\n## References to Deleted Templates")
    
    has_references = False
    for template, files in references.items():
        if files:
            has_references = True
            report.append(f"\n### {template}")
            for file in files:
                report.append(f"- {file}")
    
    if not has_references:
        report.append("\nNo references to deleted templates found.")
    
    report.append("\n## Files Updated")
    if files_updated:
        for file in files_updated:
            report.append(f"- {file}")
    else:
        report.append("No files needed updates.")
    
    report.append("\n## View Default Template Issues")
    if issues:
        for issue in issues:
            report.append(f"- {issue}")
    else:
        report.append("All view functions use unified templates as defaults.")
    
    report.append("\n## Next Steps")
    if has_references or issues:
        report.append("1. Fix any remaining references to deleted templates")
        report.append("2. Update view functions to use unified templates as defaults")
        report.append("3. Run this script again to verify all issues are resolved")
        report.append("4. Commit the changes with `git commit -m \"Complete chat template migration\"`")
    else:
        report.append("1. Commit any remaining changes with `git commit -m \"Complete chat template migration\"`")
        report.append("2. Update the documentation to reflect the completed migration")
    
    return "\n".join(report)

def main():
    """
    Main function to run the migration completion process.
    """
    print("Starting chat template migration completion...")
    
    # Find references to deleted templates
    print("Searching for references to deleted templates...")
    references = find_template_references()
    
    # Count total references
    total_references = sum(len(files) for files in references.values())
    print(f"Found {total_references} references to deleted templates.")
    
    # Update references
    files_updated = []
    if total_references > 0:
        print("Updating references...")
        files_updated = update_template_references(references)
        print(f"Updated {len(files_updated)} files.")
        
        # Re-check references after updates
        references = find_template_references()
        total_references = sum(len(files) for files in references.values())
        print(f"After updates, found {total_references} remaining references.")
    
    # Check view defaults
    print("Checking view function defaults...")
    issues = check_view_defaults()
    if issues:
        print(f"Found {len(issues)} issues with view function defaults.")
    else:
        print("All view functions use unified templates as defaults.")
    
    # Generate report
    print("Generating report...")
    report = generate_report(references, files_updated, issues)
    
    # Write report to file
    report_path = "docs/chat_migration_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report written to {report_path}")
    
    # Print summary
    if total_references > 0 or issues:
        print("\nMigration is not yet complete. Please check the report for details.")
        return 1
    else:
        print("\nMigration is complete! All references to deleted templates have been updated.")
        print("You can now commit the changes to complete the migration process.")
        return 0

if __name__ == "__main__":
    sys.exit(main())