"""
SCRIPT DE ORGANIZACIÓN DE ARCHIVOS DEL CHAT
Organiza todos los archivos generados en sus respectivas carpetas
"""
import os
import shutil
from pathlib import Path

class ChatFileOrganizer:
    def __init__(self):
        self.base_dirs = {
            'contracts': './contracts',
            'scripts': './scripts',
            'tests': './test',
            'workflows': './.github/workflows',
            'docker': './docker',
            'reports': './reports',
            'sprints': './sprints'
        }

def main():
    organizer = ChatFileOrganizer()
    organizer.create_directory_structure()
    organizer.organize_solidity_contracts()
    organizer.organize_test_files()
    organizer.organize_scripts()
    organizer.organize_workflows()
    organizer.organize_docker_files()
    organizer.organize_reports()
    print("\\n✅ ORGANIZACIÓN COMPLETADA!")

if __name__ == "__main__":
    main()