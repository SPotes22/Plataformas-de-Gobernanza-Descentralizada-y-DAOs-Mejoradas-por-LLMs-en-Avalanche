# Este script limpia un requirements.txt generado por conda para que funcione con pip
# Elimina las rutas locales (file://) y deja solo los nombres de paquetes válidos para pip

import re

input_file = 'requirements.txt'
output_file = 'requirements_clean.txt'

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

cleaned = []
for line in lines:
    line = line.strip()
    if not line or line.startswith('#'):
        continue

    # Quita los paquetes instalados con rutas locales (file://...)
    if ' @ file:///' in line:
        pkg = line.split(' @ ')[0]
        cleaned.append(pkg)
        continue

    # Quita hashes o rutas dentro de wheels
    line = re.sub(r'#sha256=[a-f0-9]+', '', line)
    cleaned.append(line.strip())

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(cleaned))

print(f'Requirements limpios guardados en {output_file}')