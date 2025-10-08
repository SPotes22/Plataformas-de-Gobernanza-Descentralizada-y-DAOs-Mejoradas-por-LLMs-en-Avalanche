
# 🏛️ StockSpider - Plataforma de Gobernanza Descentralizada

> **Web4 Financial Infrastructure - Powered by PiTech Engineering**  
> *Decentralized Governance & DAOs enhanced by LLMs on Avalanche*

[![Solidity](https://img.shields.io/badge/Solidity-0.8.23-363636?logo=solidity)](https://soliditylang.org/)
[![Avalanche](https://img.shields.io/badge/Avalanche-Fuji_Testnet-E84142?logo=avalanche)](https://avax.network)
[![Foundry](https://img.shields.io/badge/Foundry-Build%20Test%20Deploy-FF6B6B?logo=ethereum)](https://getfoundry.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Visión

PiDAO es un ecosistema completo de gobernanza descentralizada que combina **tokens ERC20 avanzados**, **sistemas de votación ponderada** y **infraestructura Web4** en la red Avalanche.

## ⚡ Características Principales

### 🪙 PiCoin Token
- **Supply Control**: Emisión limitada (6,000 - 1,000,000 tokens)
- **Staking Integrado**: Tokens stakeados para poder de voto
- **Seguridad Militar**: Auditoría completa y optimización de gas

### 🏛️ Sistema de Gobernanza
- **Votación Ponderada**: Poder de voto basado en tokens stakeados
- **Quórum Configurable**: Mínimo de participación para propuestas
- **Ejecución Automática**: Propuestas que se ejecutan automáticamente

### 🔐 Seguridad Web4
- **Octomatrix Protocol**: Arquitectura zero-trust
- **Reentrancy Protection**: Protección completa contra ataques
- **Gas Optimization**: Optimizado para costos mínimos en Avalanche

## 🚀 Quick Start

### Prerrequisitos
```bash
# Instalar Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### Deployment en Fuji Testnet
```bash
# Script de deployment automático
chmod +x scripts/auto-deploy-picoin.sh
./scripts/auto-deploy-picoin.sh
```

### Interacción con el Contrato
```bash
# Usar el script de interacción
./scripts/interact.sh

# Comandos manuales
cast call $CONTRACT "name()(string)" --rpc-url https://api.avax-test.network/ext/bc/C/rpc
cast call $CONTRACT "totalSupply()(uint256)" --rpc-url https://api.avax-test.network/ext/bc/C/rpc
```

## 📁 Estructura del Proyecto

```
PiDAO/
├── contracts/                 # Contratos Solidity
│   ├── PiCoin.sol            # Token ERC20 con staking
│   ├── PiDAOGovernance.sol   # Sistema de gobernanza
│   └── PiSign.sol            # Sistema de firma digital
├── scripts/                   # Scripts de automatización
│   ├── auto-deploy-picoin.sh # Deployment automático
│   ├── interact.sh           # Interacción con contratos
│   └── test_contract.sh      # Testing básico
├── src/                      # Fuentes principales
├── foundry.toml              # Configuración Foundry
└── deployed_address.txt      # Address del contrato desplegado ( MI PUTA CHROMEBOOK NO CORRE FORGE ENTONCES COMA MUCHA MIERDA! )
```

## 🔧 Configuración Técnica

### Redes Soportadas
- **Avalanche Fuji Testnet** (Principal para desarrollo)
- **Avalanche Mainnet** (Producción)

### Especificaciones Técnicas
```solidity
// PiCoin Token
Symbol: PICO
Decimals: 18
Supply: 6,000 - 1,000,000
Staking: Integrado para votación

// PiDAO Governance
Quórum: 1,000 tokens
Duración de votación: 1-30 días
Ejecución: Automática post-aprobación
```

## 🧪 Testing

```bash
# Ejecutar tests con Foundry
forge test -vvv

# Tests con cobertura de gas
forge test --gas-report

# Tests específicos
forge test --match-test "testStaking"
```

## 📊 Estado del Proyecto

### ✅ COMPLETADO - Sprint 7
- [x] Contrato PiCoin ERC20 con staking
- [x] Sistema básico de gobernanza
- [x] Deployment en Fuji Testnet
- [x] Scripts de automatización
- [x] Documentación técnica

### 🚧 EN PROGRESO - Sprint 8
- [ ] Sistema de votación avanzado -> visual
- [ ] Interfaz web de gobernanza -> visual
- [ ] Integración con LLMs para análisis -> endpoint creado
- [ ] Dashboard de analytics -> visual

## 🔐 Seguridad

### Auditorías Realizadas
- **SolidityScan**: Score 74.28/100
- **Manual Review**: Completado
- **Gas Optimization**: Implementado

### Prácticas de Seguridad
- Modifiers de acceso (`onlyOwner`, `nonReentrant`)
- Validación exhaustiva de inputs
- Protección contra reentrancy
- Límites de supply y tiempo

## 🌐 Explorers

- **Fuji Testnet**: [testnet.snowtrace.io](https://testnet.snowtrace.io)
- **Mainnet**: [snowtrace.io](https://snowtrace.io)

## 🤝 Contribución

I DO NOT FUCKING CARE!

## 📄 Licencia

Distribuido bajo la Licencia MIT. Ve `LICENSE` para más información.

## 👥 Equipo

**Blue Team ** - *Web4 Infrastructure & Blockchain Development*

## 🔗 Links Útiles

- [Avalanche Documentation](https://docs.avax.network/)
- [Foundry Book](https://book.getfoundry.sh/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [Core Wallet](https://core.app/)

---

**🔄 Mantenido por [PiTech Engineering](https://github.com/SPotes22) | 🏗️ Built for Web4**

# 2. package.json para metadata

```package.json
{
  "name": "pidao-governance",
  "version": "1.0.0",
  "description": "Decentralized Governance Platform on Avalanche",
  "main": "index.js",
  "scripts": {
    "deploy": "./scripts/auto-deploy-picoin.sh",
    "test": "forge test",
    "compile": "forge build",
    "interact": "./scripts/interact.sh"
  },
  "keywords": ["avalanche", "dao", "governance", "solidity", "web3"],
  "author": "PiTech Engineering",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/pitech-eng/pidao-governance"
  }
}
```
```
MIT License

Copyright (c) 2024 PiTech Engineering

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**¡ESTÁS LISTO PARA EL MUNDO WEB4! 🚀** 

Check for yourself.:
- ✅ **Documentación profesional**
- ✅ **Instrucciones claras de deployment** 
- ✅ **Estructura de proyecto estándar**
- ✅ **Badges y metadata**
- ✅ **Guías de contribución**
- ✅ **Información de seguridad**
