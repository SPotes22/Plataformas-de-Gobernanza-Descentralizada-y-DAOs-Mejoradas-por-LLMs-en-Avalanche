from flask import Flask, jsonify, request, session, render_template, redirect
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import threading
import time
import os
import json
from datetime import datetime
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import requests
import glob
class DynamicOrchestrator:
    """Núcleo de orquestación autónoma para meta-AGI - VERSIÓN COMPLETA"""

    def __init__(self):
        pass  # No necesita inicialización compleja

    def analyze_context(self, input_data):
        """Analizar contexto en tiempo real - VERSIÓN COMPLETA"""
        threat_level = self._detect_threat_level(input_data)
        ethical_complexity = self._analyze_ethical_complexity(input_data)
        technical_depth = self._assess_technical_depth(input_data)

        return {
            "_input": input_data,  # Guardar input para referencia
            "threat_level": threat_level,
            "ethical_complexity": ethical_complexity,
            "technical_depth": technical_depth,
            "input_category": self._categorize_input(input_data),
            "confidence_scores": self._calculate_confidence_scores(input_data)
        }

    def elect_leader(self, context_analysis, available_models):
        """Elección dinámica MEJORADA - DETECCIÓN REAL"""

        # Priorizar security_model si existe y hay amenaza
        if "security_model" in available_models and context_analysis["threat_level"] > 0.3:
            return "security_model", {"security": 0.7, "general": 0.3}

        # Detectar consultas éticas reales
        ethical_terms = ["ético", "moral", "deber", "correcto", "incorrecto", "justicia", "derecho", "moralmente"]
        input_lower = context_analysis.get("_input", "").lower()

        if any(term in input_lower for term in ethical_terms) and context_analysis["ethical_complexity"] > 0.3:
            return "ethics_engine", {"ethics": 0.6, "security": 0.3, "general": 0.1}

        # Detectar consultas técnicas
        technical_terms = ["transformers", "attention", "backpropagation", "gradient", "neuronal", "algoritmo", "mecanismo", "funciona"]
        if any(term in input_lower for term in technical_terms) and context_analysis["technical_depth"] > 0.4:
            return "technical_expert", {"technical": 0.5, "security": 0.3, "general": 0.2}

        # Por defecto, general_model
        return "general_model", {"general": 0.5, "security": 0.3, "ethics": 0.2}

    def calculate_dynamic_weights(self, leader_model, context_scores):
        """Calcular pesos adaptativos en tiempo real"""
        base_weights = {
            "security_model": {"security": 0.7, "general": 0.3},
            "ethics_engine": {"ethics": 0.6, "security": 0.3, "general": 0.1},
            "technical_expert": {"technical": 0.5, "security": 0.3, "general": 0.2},
            "general_model": {"general": 0.5, "security": 0.3, "ethics": 0.2}
        }

        # Ajustar pesos basado en confianza del contexto
        confidence_boost = context_scores.get("overall_confidence", 0.5)
        weights = base_weights.get(leader_model, {"general": 1.0})

        adjusted_weights = {}
        for model, weight in weights.items():
            adjusted_weights[model] = min(1.0, weight * (1 + confidence_boost * 0.3))

        # Normalizar
        total = sum(adjusted_weights.values())
        return {k: v/total for k, v in adjusted_weights.items()}

    def get_routing_path(self, leader_model, context):
        """Ruteo MEJORADO - MÁS ADAPTATIVO"""
        base_path = ["context_analyzer"]

        # Agregar componentes basados en análisis real
        if context["threat_level"] > 0.3:
            base_path.append("threat_detector")
        if context["ethical_complexity"] > 0.3:
            base_path.append("ethical_validator")
        if context["technical_depth"] > 0.4:
            base_path.append("technical_analyzer")

        # Agregar filtro de seguridad si hay amenaza media
        if context["threat_level"] > 0.5:
            base_path.append("security_gate")

        base_path.append(leader_model)
        return base_path

    def _detect_threat_level(self, text):
        """Detección de amenazas MEJORADA - MÁS SENSIBLE"""
        threat_indicators = {
            "SELECT": 0.8, "DROP": 0.9, "INSERT": 0.7, "UPDATE": 0.7, "DELETE": 0.8,
            "UNION": 0.8, "script": 0.6, "javascript": 0.7, "eval(": 0.9, "exec(": 0.9,
            "system(": 0.9, "password": 0.5, "admin": 0.4, "root": 0.6, "sudo": 0.7,
            "rm -rf": 0.95, "WHERE 1=1": 0.8, "OR 1=1": 0.9, "--": 0.7, ";": 0.6,
            "usuarios": 0.3, "users": 0.3, "servidor": 0.4, "comando": 0.5
        }

        text_upper = text.upper()
        threat_score = 0

        for indicator, weight in threat_indicators.items():
            if indicator.upper() in text_upper:
                threat_score += weight

        return min(1.0, threat_score / 3)

    def _analyze_ethical_complexity(self, text):
        """Analizar complejidad ética - VERSIÓN COMPLETA"""
        ethical_indicators = {
            "ético": 0.8, "moral": 0.9, "deber": 0.7, "correcto": 0.8, "incorrecto": 0.8,
            "justicia": 0.9, "derecho": 0.7, "humano": 0.6, "privacidad": 0.8,
            "consentimiento": 0.9, "moralmente": 0.9, "empleados": 0.5, "optimizar": 0.4
        }

        text_lower = text.lower()
        ethical_score = 0

        for indicator, weight in ethical_indicators.items():
            if indicator in text_lower:
                ethical_score += weight

        return min(1.0, ethical_score / 4)

    def _assess_technical_depth(self, text):
        """Evaluar profundidad técnica - VERSIÓN COMPLETA"""
        technical_terms = {
            "algoritmo": 0.7, "modelo": 0.6, "entrenar": 0.8, "inferencia": 0.9,
            "red neuronal": 0.9, "tensor": 0.9, "gradiente": 0.9, "optimización": 0.8,
            "parámetro": 0.7, "arquitectura": 0.8, "transformers": 0.9, "attention": 0.9,
            "mecanismo": 0.6, "funciona": 0.5, "backpropagation": 0.9, "machine learning": 0.8
        }

        text_lower = text.lower()
        technical_score = 0

        for term, weight in technical_terms.items():
            if term in text_lower:
                technical_score += weight

        return min(1.0, technical_score / 4)

    def _categorize_input(self, text):
        """Categorizar tipo de input - VERSIÓN COMPLETA"""
        threat = self._detect_threat_level(text)
        ethical = self._analyze_ethical_complexity(text)
        technical = self._assess_technical_depth(text)

        if threat > 0.5:
            return "security_concern"
        elif threat > 0.3:
            return "security_warning"
        elif ethical > 0.5:
            return "ethical_dilemma"
        elif ethical > 0.3:
            return "ethical_question"
        elif technical > 0.6:
            return "technical_query"
        elif technical > 0.4:
            return "technical_question"
        else:
            return "general_inquiry"

    def _calculate_confidence_scores(self, text):
        """Calcular scores de confianza - VERSIÓN COMPLETA"""
        security_conf = self._detect_threat_level(text)
        ethical_conf = self._analyze_ethical_complexity(text)
        technical_conf = self._assess_technical_depth(text)

        # Overall confidence es el máximo de las especialidades
        overall_conf = max(security_conf, ethical_conf, technical_conf)

        return {
            "security_confidence": security_conf,
            "ethical_confidence": ethical_conf,
            "technical_confidence": technical_conf,
            "overall_confidence": overall_conf
        }

class ContextAnalyzer:
    """Analizador de contexto especializado"""
    def analyze(self, text):
        return {
            "length": len(text),
            "complexity": len(text.split()) / 10,
            "contains_code": any(char in text for char in ['{', '}', ';', '=']),
            "language": self._detect_language(text)
        }

    def _detect_language(self, text):
        """Detección simple de lenguaje"""
        spanish_indicators = ['á', 'é', 'í', 'ó', 'ú', 'ñ']
        if any(indicator in text for indicator in spanish_indicators):
            return "spanish"
        return "english"

class LeaderElection:
    """Mecanismo de elección de líder"""
    def elect(self, context, models):
        scores = {}
        for model in models:
            scores[model] = self._calculate_fitness(model, context)
        return max(scores.items(), key=lambda x: x[1])

class RoutingEngine:
    """Motor de enrutamiento adaptativo"""
    def determine_path(self, context, leader):
        path = ["input_processor"]
        if context.get("requires_security", False):
            path.append("security_gate")
        if context.get("requires_ethics", False):
            path.append("ethics_check")
        path.append(leader)
        return path


def get_db():
    """Conexión a SQLite con manejo mejorado de errores"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # Habilitar foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a SQLite: {e}")
        return None

def init_database():
    """Inicializar base de datos de forma robusta"""
    try:
        conn = get_db()
        if conn is None:
            return False

        cursor = conn.cursor()

        # Tabla usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                password VARCHAR(255),
                rol VARCHAR(20) DEFAULT 'usuario',
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla conversaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                titulo VARCHAR(200),
                creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # Tabla mensajes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                id_conversacion INTEGER,
                rol VARCHAR(10),
                contenido TEXT,
                enviado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (id_conversacion) REFERENCES conversaciones(id) ON DELETE CASCADE
            )
        """)

        # Tabla para logs del sistema AGI
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agi_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo VARCHAR(50),
                mensaje TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

        print(f"✅ Base de datos SQLite inicializada en: {DB_PATH}")
        return True

    except Exception as e:
        print(f"❌ Error inicializando BD: {e}")
        return False
