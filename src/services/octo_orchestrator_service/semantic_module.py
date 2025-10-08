from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    class EnhancedSemanticService:
        def __init__(self):
            self.enabled = True
            self.vectorizer = None
            self.concepts = []

            try:
                self._initialize_semantic_system()
                print("✅ Servicio semántico mejorado inicializado")
            except Exception as e:
                print(f"❌ Error servicio semántico: {e}")
                self.enabled = False

        def _initialize_semantic_system(self):
            """Sistema semántico mejorado con más conceptos"""
            self.concepts = [
                "inteligencia artificial", "algoritmo machine learning", "red neuronal profunda",
                "procesamiento lenguaje natural", "razonamiento automático", "sistema autónomo",
                "orquestación inteligente", "ética artificial", "seguridad cibernética",
                "análisis contextual", "respuesta coherente", "arquitectura multinivel",
                "tin tan sabio", "experto técnico", "consejero ético", "guardián seguridad",
                "diálogo inteligente", "comprensión semántica", "adaptación conversacional",
                "aprendizaje automático", "redes neuronales", "procesamiento datos",
                "toma de decisiones", "razonamiento lógico", "ética tecnología",
                "seguridad informática", "privacidad datos", "algoritmos inteligentes"
            ]

            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words=['de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se'],
                max_features=100
            )

            # Entrenar el vectorizer
            self.vectorizer.fit(self.concepts)

        def semantic_analysis(self, text: str) -> dict:
            """Análisis semántico completo"""
            if not self.enabled:
                return {"error": "Servicio no disponible"}

            try:
                text_vector = self.vectorizer.transform([text])
                concept_vectors = self.vectorizer.transform(self.concepts)
                similarities = cosine_similarity(text_vector, concept_vectors)[0]

                concept_similarities = []
                for i, similarity in enumerate(similarities):
                    if similarity > 0.1:
                        concept_similarities.append({
                            "concept": self.concepts[i],
                            "similarity": float(similarity),
                            "category": self._categorize_concept(self.concepts[i])
                        })

                concept_similarities.sort(key=lambda x: x["similarity"], reverse=True)
                top_concepts = concept_similarities[:3]

                return {
                    "input": text,
                    "top_concepts": top_concepts,
                    "semantic_density": len(top_concepts),
                    "primary_concept": top_concepts[0]["concept"] if top_concepts else "general",
                    "confidence": top_concepts[0]["similarity"] if top_concepts else 0.0,
                    "method": "tfidf_cosine"
                }

            except Exception as e:
                return {"error": f"Error en análisis: {str(e)}"}

        def enhance_response(self, user_input: str, original_response: str, personality: str) -> str:
            """Mejora de respuesta con análisis semántico"""
            analysis = self.semantic_analysis(user_input)

            if "error" in analysis or not analysis.get("top_concepts"):
                return original_response

            top_concepts = analysis["top_concepts"]
            primary_concept = analysis["primary_concept"]
            confidence = analysis["confidence"]

            enhancements = {
                "tin_tan_sabio": f"\n\n🔍 **Perspectiva semántica**: Desde '{primary_concept}' (confianza: {confidence:.2f}), se revelan capas adicionales de significado contextual.",
                "technical_expert": f"\n\n🔧 **Contexto técnico**: Enmarcado en '{primary_concept}', el análisis semántico refuerza la precisión técnica del razonamiento.",
                "ethical_advisor": f"\n\n⚖️ **Dimensión ética**: Considerando '{primary_concept}', se integran consideraciones morales y valores relevantes.",
                "security_guardian": f"\n\n🛡️ **Marco de seguridad**: Desde '{primary_concept}', se aplican filtros de verificación y consideraciones protectoras."
            }

            enhancement = enhancements.get(personality, enhancements["tin_tan_sabio"])

            if confidence > 0.2:
                return original_response + enhancement
            else:
                return original_response

        def quick_enhance(self, user_input: str, original_response: str) -> str:
            """Mejora rápida por palabras clave"""
            input_lower = user_input.lower()
            matched_concepts = []

            for concept in self.concepts:
                concept_words = concept.split()
                matches = sum(1 for word in concept_words if word in input_lower)
                if matches >= 1:
                    matched_concepts.append(concept)

            if matched_concepts:
                enhancement = f"\n\n🔍 **Relacionado con**: {', '.join(matched_concepts[:2])}"
                return original_response + enhancement

            return original_response

        def _categorize_concept(self, concept: str) -> str:
            """Categorización de conceptos"""
            concept_lower = concept.lower()

            if any(word in concept_lower for word in ['ético', 'moral', 'consejero']):
                return "ético"
            elif any(word in concept_lower for word in ['seguridad', 'guardián', 'protección']):
                return "seguridad"
            elif any(word in concept_lower for word in ['técnico', 'algoritmo', 'machine', 'red neuronal']):
                return "técnico"
            elif any(word in concept_lower for word in ['sabio', 'razonamiento', 'inteligencia']):
                return "sabio"
            else:
                return "general"

    semantic_service = EnhancedSemanticService()

except ImportError as e:
    print(f"⚠️ Scikit-learn no disponible: {e}")
    semantic_service = None
