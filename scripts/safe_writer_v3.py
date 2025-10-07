#!/usr/bin/env python3
"""
SafeFileWriter v3.0 - Con Rollback Controlado y Avalanche Integration
Evolución directa desde PiCoin MVP 2022 → AGI Governance 2025
"""

import os
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import asyncio
from datetime import datetime
import aiofiles
from web3 import Web3
import requests



def setup_docker_environment():
    """Configuración automática para Docker"""
    if os.path.exists('/.dockerenv'):
        print("🐳 Ejecutando en entorno Docker")
        
        # Configurar paths para Docker
        base_path = Path("/app")
        backup_dir = base_path / "arachne_backups"
        backup_dir.mkdir(exist_ok=True)
        
        return base_path
    return Path(".")

class ArachneSafeWriter:
    """
    Safe File Writer con rollback controlado y preparado para Avalanche
    Evolución: PiCoin MVP (2022) → SpiderStock (2024) → AGI Governance (2025)
    """
    
    def __init__(self, base_path: str = ".", avalanche_rpc: str = None):
        self.base_path = Path(base_path)
        self.entropy_threshold = 3.14
        
        # Sistema de rollback mejorado
        self.backup_manager = BackupManager(self.base_path)
        self.vector_space = self._init_vector_space()
        
        # Integración Web3/Avalanche
        self.avalanche_client = AvalancheClient(avalanche_rpc) if avalanche_rpc else None
        
        # Estado transaccional
        self.pending_transactions = {}
        self.transaction_timeout = 30
        
        self.logger = self._setup_arachne_logger()
    
    def _setup_arachne_logger(self) -> logging.Logger:
        """Logger con estilo Arachne (desde 2022)"""
        logger = logging.getLogger('ArachneSafeWriter')
        
        # Handler para CI/CD
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '🕷️ [ARACHNE-CI/CD] %(asctime)s - %(levelname)s - %(message)s'
        ))
        
        # Handler para archivo (trazabilidad histórica)
        file_handler = logging.FileHandler('logs/arachne_safe_writer.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s | Hash: %(filename)s@%(lineno)d'
        ))
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        
        return logger
    
    def _init_vector_space(self) -> Dict:
        """Espacio vectorial 6x128 evolucionado desde PiCoin MVP"""
        return {
            'que': [0] * 128,        # Propósito semántico
            'porque': [0] * 128,     # Justificación ética  
            'paraque': [0] * 128,    # Objetivo funcional
            'como': [0] * 128,       # Metodología técnica
            'cuando': [0] * 128,     # Temporalidad ejecutiva
            'donde': [0] * 128       # Contexto arquitectónico
        }
    
    async def transactional_write(self, file_name: str, content: str, file_type: str = "py") -> Dict:
        """
        Escritura transaccional con rollback automático
        Patrón: Prepare → Validate → Commit/Rollback
        """
        transaction_id = self._generate_transaction_id()
        
        try:
            # FASE 1: PREPARE
            self.pending_transactions[transaction_id] = {
                'file_name': file_name,
                'content': content,
                'file_type': file_type,
                'start_time': datetime.now(),
                'status': 'preparing'
            }
            
            # Crear backup del archivo existente
            file_path = self.base_path / file_name
            if file_path.exists():
                backup_path = await self.backup_manager.create_backup(file_path, transaction_id)
                self.pending_transactions[transaction_id]['backup_path'] = backup_path
            
            # FASE 2: VALIDATE
            validation_result = await self._validate_write_transaction(content, file_type)
            if not validation_result['valid']:
                await self._rollback_transaction(transaction_id)
                return {
                    'status': 'validation_failed',
                    'transaction_id': transaction_id,
                    'error': validation_result['error'],
                    'entropy': validation_result.get('entropy')
                }
            
            # FASE 3: COMMIT
            commit_result = await self._commit_transaction(transaction_id, content)
            
            self.logger.info(f"✅ TRANSACTION COMMITTED: {transaction_id} - {file_name}")
            
            return {
                'status': 'success',
                'transaction_id': transaction_id,
                'entropy': validation_result['entropy'],
                'vector_updated': True,
                'avalanche_tx': commit_result.get('avalanche_tx')
            }
            
        except Exception as e:
            # FASE 4: ROLLBACK DE EMERGENCIA
            await self._emergency_rollback(transaction_id, str(e))
            return {
                'status': 'transaction_failed',
                'transaction_id': transaction_id,
                'error': str(e)
            }
    
    async def _validate_write_transaction(self, content: str, file_type: str) -> Dict:
        """Validación completa de la transacción"""
        # 1. Validar entropía
        entropy = self._calculate_content_entropy(content)
        if entropy >= self.entropy_threshold:
            return {
                'valid': False,
                'error': f'Entropía excedida: {entropy:.2f}% >= {self.entropy_threshold}%',
                'entropy': entropy
            }
        
        # 2. Validar seguridad del contenido
        security_scan = self._security_scan_content(content)
        if not security_scan['safe']:
            return {
                'valid': False,
                'error': f'Contenido no seguro: {security_scan["threats"]}',
                'entropy': entropy
            }
        
        # 3. Validar integridad semántica (para archivos de configuración)
        if file_type in ['json', 'yaml', 'config']:
            semantic_check = await self._validate_semantic_integrity(content, file_type)
            if not semantic_check['valid']:
                return {
                    'valid': False,
                    'error': f'Integridad semántica: {semantic_check["error"]}',
                    'entropy': entropy
                }
        
        return {
            'valid': True,
            'entropy': entropy,
            'security_scan': security_scan
        }
    
    async def _commit_transaction(self, transaction_id: str, content: str) -> Dict:
        """Commit de la transacción"""
        transaction = self.pending_transactions[transaction_id]
        file_path = self.base_path / transaction['file_name']
        
        # Escribir archivo
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        # Actualizar vector space
        await self._update_vector_space(file_path, transaction['file_type'])
        
        # Opcional: Registrar en Avalanche
        avalanche_tx = None
        if self.avalanche_client:
            try:
                avalanche_tx = await self.avalanche_client.record_file_write(
                    file_path.name,
                    self._calculate_content_hash(content),
                    transaction_id
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Avalanche recording failed: {e}")
        
        # Limpiar transacción
        self.pending_transactions[transaction_id]['status'] = 'committed'
        self.pending_transactions[transaction_id]['end_time'] = datetime.now()
        
        return {'avalanche_tx': avalanche_tx}
    
    async def _rollback_transaction(self, transaction_id: str) -> None:
        """Rollback controlado de transacción"""
        transaction = self.pending_transactions.get(transaction_id)
        if not transaction:
            return
        
        try:
            # Restaurar backup si existe
            backup_path = transaction.get('backup_path')
            if backup_path and backup_path.exists():
                file_path = self.base_path / transaction['file_name']
                await self.backup_manager.restore_backup(backup_path, file_path)
            
            # Revertir vector space si fue actualizado
            if transaction.get('vector_updated'):
                await self._revert_vector_space_update(transaction)
            
            self.logger.info(f"🔁 ROLLBACK COMPLETADO: {transaction_id}")
            
        except Exception as e:
            self.logger.error(f"❌ ROLLBACK FALLIDO: {transaction_id} - {e}")
        
        finally:
            # Limpiar recursos
            if 'backup_path' in transaction:
                await self.backup_manager.cleanup_backup(transaction['backup_path'])
            
            transaction['status'] = 'rolled_back'
            transaction['end_time'] = datetime.now()

class BackupManager:
    """Gestor de backups para rollback seguro"""
    
    def __init__(self, base_path: Path):
        self.backup_dir = base_path / "arachne_backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    async def create_backup(self, file_path: Path, transaction_id: str) -> Path:
        """Crear backup seguro con transaction ID"""
        backup_name = f"{file_path.stem}_backup_{transaction_id}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        async with aiofiles.open(file_path, 'rb') as src, \
                   aiofiles.open(backup_path, 'wb') as dst:
            content = await src.read()
            await dst.write(content)
        
        return backup_path
    
    async def restore_backup(self, backup_path: Path, target_path: Path) -> None:
        """Restaurar backup a ubicación original"""
        async with aiofiles.open(backup_path, 'rb') as src, \
                   aiofiles.open(target_path, 'wb') as dst:
            content = await src.read()
            await dst.write(content)
    
    async def cleanup_backup(self, backup_path: Path) -> None:
        """Limpiar backup después de transacción completada"""
        try:
            if backup_path.exists():
                backup_path.unlink()
        except Exception as e:
            logging.warning(f"Cleanup backup failed: {e}")

class AvalancheClient:
    """Cliente para integración con Avalanche (opcional)"""
    
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        # Configuración básica para C-Chain
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    async def record_file_write(self, file_name: str, content_hash: str, transaction_id: str) -> Optional[str]:
        """Registrar escritura de archivo en Avalanche (para auditoría)"""
        # Implementación básica - expandir según contrato específico
        try:
            # Aquí iría la lógica para interactuar con tu smart contract
            # Por ahora solo mock
            return f"0x{content_hash[:64]}"
        except Exception as e:
            raise Exception(f"Avalanche recording error: {e}")

# Instancia global mejorada
arachne_writer = ArachneSafeWriter()

# Función de compatibilidad para CI/CD existente
def cicd_safe_write(file_name: str, content: str, file_type: str = "py") -> Dict:
    """Wrapper síncrono para integración inmediata en CI/CD"""
    return asyncio.run(arachne_writer.transactional_write(file_name, content, file_type))
