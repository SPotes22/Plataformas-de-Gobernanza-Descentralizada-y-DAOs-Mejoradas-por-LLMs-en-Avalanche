# test_entropy.py
with open('avalanche_logger_daemon.py', 'r') as f:
    content = f.read()

# Calcular entropía manualmente
import math
char_freq = {}
for char in content:
    char_freq[char] = char_freq.get(char, 0) + 1

entropy = 0.0
total_chars = len(content)
for count in char_freq.values():
    prob = count / total_chars
    entropy -= prob * math.log2(prob)

print(f"🎯 Entropía del daemon: {entropy:.2f}% / 3.14%")
print(f"✅ {'DENTRO DEL LÍMITE' if entropy <= 3.14 else 'EXCEDIDO'}")
