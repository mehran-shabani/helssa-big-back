#!/usr/bin/env python3
"""
HELSSA Agents Structure Validator
Validates that all agent applications have the correct structure
"""

import os
import json
from pathlib import Path

def check_file_exists(path):
    """Check if file exists and return result"""
    return {
        'path': str(path),
        'exists': path.exists(),
        'size': path.stat().st_size if path.exists() else 0
    }

def validate_app_structure(app_path):
    """Validate structure of a single application"""
    app_name = app_path.name
    results = {
        'app_name': app_name,
        'valid': True,
        'issues': [],
        'files': {}
    }
    
    # Required files
    required_files = [
        'PLAN.md',
        'CHECKLIST.json', 
        'PROGRESS.json',
        'LOG.md',
        'README.md',
        'app_code/__init__.py',
        'app_code/models.py',
        'app_code/views.py', 
        'app_code/serializers.py',
        'app_code/urls.py',
        'app_code/admin.py',
        'app_code/permissions.py',
        'app_code/cores/__init__.py',
        'app_code/cores/api_ingress.py',
        'app_code/cores/text_processor.py',
        'app_code/cores/speech_processor.py',
        'app_code/cores/orchestrator.py',
        'deployment/settings_additions.py',
        'deployment/urls_additions.py',
        'deployment/requirements_additions.txt'
    ]
    
    for file_path in required_files:
        full_path = app_path / file_path
        file_result = check_file_exists(full_path)
        results['files'][file_path] = file_result
        
        if not file_result['exists']:
            results['valid'] = False
            results['issues'].append(f"Missing required file: {file_path}")
    
    # Check JSON files are valid
    json_files = ['CHECKLIST.json', 'PROGRESS.json']
    for json_file in json_files:
        json_path = app_path / json_file
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                results['valid'] = False
                results['issues'].append(f"Invalid JSON in {json_file}: {str(e)}")
    
    return results

def main():
    """Main validation function"""
    agents_dir = Path('/workspace/HELSSA_AGENTS')
    
    if not agents_dir.exists():
        print("❌ HELSSA_AGENTS directory not found!")
        return
    
    print("🔍 Validating HELSSA Agents Structure...\n")
    
    # List of expected applications
    expected_apps = [
        'patient_chatbot',
        'doctor-chatbot-a', 
        'doctor-dashboard',
        'soapify',
        'patient_records',
        'appointment_scheduler',
        'telemedicine_core', 
        'prescription_system',
        'visit_management',
        'unified_auth_integration',
        'unified_billing_integration',
        'unified_ai_integration',
        'admin_dashboard',
        'analytics_system',
        'notification_system'
    ]
    
    results = {}
    total_valid = 0
    
    for app_name in expected_apps:
        app_path = agents_dir / app_name
        
        if not app_path.exists():
            print(f"⚠️  {app_name}: Directory not found")
            continue
            
        result = validate_app_structure(app_path)
        results[app_name] = result
        
        if result['valid']:
            print(f"✅ {app_name}: Structure valid")
            total_valid += 1
        else:
            print(f"❌ {app_name}: Issues found")
            for issue in result['issues']:
                print(f"   - {issue}")
    
    print(f"\n📊 Summary:")
    print(f"Total applications: {len(expected_apps)}")
    print(f"Valid structures: {total_valid}")
    print(f"Invalid structures: {len(expected_apps) - total_valid}")
    
    # Check core documentation files
    print(f"\n📚 Core Documentation:")
    core_docs = [
        'README_AGENTS.md',
        'PROJECT_TREE_COMPLETE.md',
        'AGENT_INSTRUCTIONS.md',
        'CORE_ARCHITECTURE.md',
        'SECURITY_POLICIES.md',
        'AGENT_PROMPT_TEMPLATE.md'
    ]
    
    for doc in core_docs:
        doc_path = agents_dir / doc
        if doc_path.exists():
            print(f"✅ {doc}")
        else:
            print(f"❌ {doc}")
    
    # Check HELSSA documentation
    helssa_docs_path = agents_dir / 'HELSSA_DOCS'
    if helssa_docs_path.exists():
        print(f"✅ HELSSA_DOCS directory exists")
        doc_count = len(list(helssa_docs_path.glob('*.md')))
        print(f"   📄 Contains {doc_count} documentation files")
    else:
        print(f"❌ HELSSA_DOCS directory missing")
    
    # Generate detailed report
    report_path = agents_dir / 'validation_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    if total_valid == len(expected_apps):
        print("\n🎉 All applications have valid structure!")
        return True
    else:
        print(f"\n⚠️  {len(expected_apps) - total_valid} applications need attention")
        return False

if __name__ == "__main__":
    main()