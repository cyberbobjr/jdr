#!/usr/bin/env python3
"""
JSON to YAML Migration Tool for JdR Game Data

This script converts all JSON game data files to YAML format
for better maintainability and human readability.

Author: Kilo Code
Date: 2025-11-12
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any

# Add the back directory to the path to import config
sys.path.append(str(Path(__file__).parent.parent / "back"))

class JSONToYAMLMigrator:
    """Migrates JSON game data files to YAML format"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.backup_dir = self.data_dir / "json_backup"
        
        # Files to migrate (relative to data_dir)
        self.files_to_migrate = [
            "combat_system.json",
            "equipment.json", 
            "races_and_cultures.json",
            "skill_groups.json",
            "skills_affinities.json",
            "skills_for_llm.json",
            "spells.json",
            "stats.json"
        ]
        
    def create_backup(self) -> None:
        """Create backup directory for original JSON files"""
        self.backup_dir.mkdir(exist_ok=True)
        print(f"✅ Created backup directory: {self.backup_dir}")
        
    def backup_json_files(self) -> None:
        """Backup all JSON files before migration"""
        print("📦 Backing up JSON files...")
        for filename in self.files_to_migrate:
            json_path = self.data_dir / filename
            if json_path.exists():
                backup_path = self.backup_dir / filename
                import shutil
                shutil.copy2(json_path, backup_path)
                print(f"  ✅ Backed up: {filename}")
            else:
                print(f"  ⚠️  File not found: {filename}")
                
    def load_json_file(self, filepath: Path) -> Dict[str, Any]:
        """Load and parse JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return {}
            
    def save_yaml_file(self, filepath: Path, data: Dict[str, Any]) -> bool:
        """Save data to YAML file with proper formatting"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(
                    data, 
                    f, 
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    indent=2,
                    width=80
                )
            return True
        except Exception as e:
            print(f"❌ Error saving {filepath}: {e}")
            return False
            
    def migrate_file(self, filename: str) -> bool:
        """Migrate a single JSON file to YAML"""
        json_path = self.data_dir / filename
        yaml_path = self.data_dir / filename.replace('.json', '.yaml')
        
        if not json_path.exists():
            print(f"  ⚠️  Source file not found: {filename}")
            return False
            
        print(f"  🔄 Migrating: {filename} -> {yaml_path.name}")
        
        # Load JSON data
        data = self.load_json_file(json_path)
        if not data:
            return False
            
        # Save as YAML
        success = self.save_yaml_file(yaml_path, data)
        if success:
            print(f"  ✅ Successfully migrated: {filename}")
            # Remove original JSON file
            json_path.unlink()
            print(f"  🗑️  Removed original: {filename}")
        else:
            print(f"  ❌ Failed to migrate: {filename}")
            
        return success
        
    def validate_yaml_file(self, filepath: Path) -> bool:
        """Validate that YAML file can be loaded correctly"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"❌ Validation failed for {filepath}: {e}")
            return False
            
    def migrate_all_files(self) -> Dict[str, bool]:
        """Migrate all JSON files to YAML"""
        print("🚀 Starting JSON to YAML migration...")
        
        results = {}
        
        for filename in self.files_to_migrate:
            success = self.migrate_file(filename)
            results[filename] = success
            
        return results
        
    def validate_migrated_files(self) -> Dict[str, bool]:
        """Validate all migrated YAML files"""
        print("\n🔍 Validating migrated YAML files...")
        
        validation_results = {}
        
        for filename in self.files_to_migrate:
            yaml_filename = filename.replace('.json', '.yaml')
            yaml_path = self.data_dir / yaml_filename
            
            if yaml_path.exists():
                is_valid = self.validate_yaml_file(yaml_path)
                validation_results[yaml_filename] = is_valid
                status = "✅" if is_valid else "❌"
                print(f"  {status} {yaml_filename}")
            else:
                print(f"  ⚠️  File not found: {yaml_filename}")
                validation_results[yaml_filename] = False
                
        return validation_results
        
    def generate_migration_report(self, migration_results: Dict[str, bool], 
                                validation_results: Dict[str, bool]) -> None:
        """Generate migration report"""
        print("\n📊 MIGRATION REPORT")
        print("=" * 50)
        
        total_files = len(self.files_to_migrate)
        successful_migrations = sum(1 for success in migration_results.values() if success)
        successful_validations = sum(1 for valid in validation_results.values() if valid)
        
        print(f"Total files: {total_files}")
        print(f"Successful migrations: {successful_migrations}/{total_files}")
        print(f"Successful validations: {successful_validations}/{total_files}")
        
        print("\nDetailed Results:")
        for filename in self.files_to_migrate:
            yaml_filename = filename.replace('.json', '.yaml')
            migration_status = "✅" if migration_results.get(filename, False) else "❌"
            validation_status = "✅" if validation_results.get(yaml_filename, False) else "❌"
            print(f"  {migration_status} {filename} -> {yaml_filename} {validation_status}")
            
        if successful_migrations == total_files and successful_validations == total_files:
            print("\n🎉 Migration completed successfully!")
        else:
            print("\n⚠️  Migration completed with some issues. Please check the report above.")
            
    def run_migration(self) -> None:
        """Run the complete migration process"""
        print("🎯 JSON to YAML Migration Tool for JdR Game Data")
        print("=" * 60)
        
        # Create backup
        self.create_backup()
        self.backup_json_files()
        
        # Migrate files
        migration_results = self.migrate_all_files()
        
        # Validate migrated files
        validation_results = self.validate_migrated_files()
        
        # Generate report
        self.generate_migration_report(migration_results, validation_results)
        
        print(f"\n💾 Original JSON files are backed up in: {self.backup_dir}")
        print("📝 Please update your code to reference .yaml files instead of .json files")


def main():
    """Main entry point"""
    # Check if we're in the right directory
    if not Path("data").exists():
        print("❌ Error: 'data' directory not found. Please run this script from the project root.")
        sys.exit(1)
        
    migrator = JSONToYAMLMigrator()
    migrator.run_migration()


if __name__ == "__main__":
    main()