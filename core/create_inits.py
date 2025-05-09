# Small helper to create __init__.py inside needed folders
import os

folders = [
    'core',
    'ui',
    'plugins',
    'plugins/helmet_detect',
    'plugins/fire_detect',
    'plugins/faceid_recog',
    'plugins/intrusion_detect',
    'industrial',
    'ml_ops',
    'tests',
]

for folder in folders:
    init_file = os.path.join(folder, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            pass

print("__init__.py files created.")
