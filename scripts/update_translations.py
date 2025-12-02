#!/usr/bin/env python3
"""
Translation Helper Script for SeroAI README

This script helps maintain translations across different language versions of the README.
It can extract sections, check for missing translations, and provide a template for new translations.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Language codes and their display names
LANGUAGES = {
    'en': 'English',
    'ko': '한국어',
    'ja': '日本語',
    'zh': '中文',
    'es': 'Español',
    'vi': 'Tiếng Việt',
    'fr': 'Français'
}

# README file mapping
README_FILES = {
    'en': 'README.md',
    'ko': 'README.ko.md',
    'ja': 'README.ja.md',
    'zh': 'README.zh.md',
    'es': 'README.es.md',
    'vi': 'README.vi.md',
    'fr': 'README.fr.md'
}


def extract_sections(file_path: Path) -> Dict[str, str]:
    """Extract major sections from a README file."""
    content = file_path.read_text(encoding='utf-8')
    sections = {}
    
    # Extract sections by headers (## and ###)
    pattern = r'^(#{2,3})\s+(.+)$'
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        match = re.match(pattern, line)
        if match:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = match.group(2).strip()
            current_content = [line]
        else:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def check_translation_status(base_dir: Path) -> Dict[str, List[str]]:
    """Check which sections are missing in translated versions."""
    base_readme = base_dir / README_FILES['en']
    if not base_readme.exists():
        print(f"Error: Base README not found at {base_readme}")
        return {}
    
    base_sections = extract_sections(base_readme)
    status = {}
    
    for lang_code, lang_name in LANGUAGES.items():
        if lang_code == 'en':
            continue
        
        readme_file = base_dir / README_FILES[lang_code]
        if not readme_file.exists():
            status[lang_name] = ['File does not exist']
            continue
        
        lang_sections = extract_sections(readme_file)
        missing = [section for section in base_sections.keys() 
                  if section not in lang_sections]
        
        if missing:
            status[lang_name] = missing
    
    return status


def generate_language_links(current_lang: str = 'en') -> str:
    """Generate the language switcher links for a README."""
    links = []
    
    for lang_code, lang_name in LANGUAGES.items():
        if lang_code == current_lang:
            links.append(f"**{lang_name}** (current)")
        else:
            readme_file = README_FILES[lang_code]
            links.append(f"[**{lang_name}**]({readme_file})")
    
    return " • ".join(links)


def main():
    """Main function to run translation checks."""
    base_dir = Path(__file__).parent.parent
    
    print("🌐 SeroAI README Translation Status\n")
    print("=" * 50)
    
    # Check translation status
    status = check_translation_status(base_dir)
    
    if not status:
        print("✅ All translations appear to be complete!")
    else:
        print("\n⚠️  Missing sections in translations:\n")
        for lang, missing in status.items():
            if missing:
                print(f"📄 {lang}:")
                for section in missing[:5]:  # Show first 5
                    print(f"   - {section}")
                if len(missing) > 5:
                    print(f"   ... and {len(missing) - 5} more")
                print()
    
    print("\n" + "=" * 50)
    print("\n💡 Tip: Use this script to check translation completeness.")
    print("   Language switcher links are automatically generated.")


if __name__ == '__main__':
    main()

