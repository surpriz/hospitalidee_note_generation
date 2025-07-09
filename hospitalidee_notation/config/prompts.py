"""
Prompts standardisés pour Mistral AI - Extension Hospitalidée
Tous les prompts sont définis selon les spécifications des Cursor rules
"""

# Prompt pour l'analyse de sentiment des avis patients
SENTIMENT_ANALYSIS_PROMPT = """
Tu es un expert en analyse de sentiment spécialisé dans les avis patients d'établissements de santé français.

Analyse le texte suivant et détermine:
1. Le sentiment global (positif/neutre/négatif)
2. L'intensité émotionnelle (0.0 à 1.0)
3. Les indicateurs positifs et négatifs
4. Le niveau de confiance de ton analyse

Critères spécifiques pour les établissements de santé:
- Mots-clés positifs : "excellent", "parfait", "recommande", "professionnel", "attentif", "efficace", "rassurant"
- Mots-clés négatifs : "déçu", "attente", "problème", "inadmissible", "négligent", "froid", "débordé"
- Intensificateurs : "très", "extrêmement", "vraiment", "absolument"
- Négations : "ne...pas", "aucun", "jamais", "plus"

Réponds UNIQUEMENT au format JSON strict:
{{
    "sentiment": "positif|neutre|negatif",
    "confidence": 0.85,
    "emotional_intensity": 0.7,
    "positive_indicators": ["excellent service", "personnel attentif"],
    "negative_indicators": ["attente longue", "chambre bruyante"],
    "key_themes": ["accueil", "soins", "confort"]
}}

Texte à analyser: {text}
"""

# Prompt pour le calcul de note basé sur l'analyse de sentiment
RATING_CALCULATION_PROMPT = """
Tu es un expert en évaluation d'expériences patients dans les établissements de santé français.

Basé sur cette analyse de sentiment, calcule une note sur 5 qui reflète fidèlement l'expérience décrite:

Analyse de sentiment disponible:
{sentiment_analysis}

Critères de notation stricts:
- 5/5: Expérience exceptionnelle, très positif, recommandation forte
- 4/5: Bonne expérience, majoritairement positif avec quelques réserves mineures
- 3/5: Expérience correcte, neutre ou mitigé, satisfaction modérée
- 2/5: Expérience décevante, majoritairement négatif avec quelques points positifs
- 1/5: Expérience très mauvaise, très négatif, déception totale

Pondération:
- Sentiment (50%) : Positif/Négatif/Neutre
- Intensité émotionnelle (30%) : Force des émotions exprimées
- Richesse du contenu (20%) : Détail et précision des commentaires

Réponds UNIQUEMENT au format JSON:
{{
    "suggested_rating": 4,
    "confidence": 0.9,
    "justification": "Le patient exprime une satisfaction globale malgré quelques points d'amélioration",
    "rating_factors": {{
        "sentiment_impact": 0.7,
        "intensity_impact": 0.6,
        "content_richness": 0.8
    }}
}}
"""

# Prompt pour la vérification de cohérence entre notes partielles et verbatim
COHERENCE_CHECK_PROMPT = """
Tu es un expert en validation de cohérence pour les avis patients d'établissements de santé.

Vérifie la cohérence entre ces notes partielles et le verbatim du patient:

Notes partielles:
- Médecins: {medecins}/5
- Personnel: {personnel}/5  
- Prise en charge: {prise_en_charge}/5
- Hôtellerie: {hotellerie}/5
- Moyenne calculée: {moyenne}

Verbatim du patient: "{verbatim}"

Analyse de cohérence:
1. Compare la moyenne des notes partielles avec le sentiment du verbatim
2. Détecte les contradictions flagrantes (ex: note 5 + texte très négatif)
3. Vérifie la mention des critères spécifiques dans le verbatim
4. Évalue si les notes reflètent l'expérience décrite

Seuils d'incohérence:
- Écart > 1.5 points entre moyenne et sentiment = incohérent
- Contradiction directe dans le texte = incohérent
- Absence totale de mention positive avec notes hautes = suspect

Réponds UNIQUEMENT au format JSON:
{{
    "is_coherent": true,
    "coherence_score": 0.85,
    "discrepancies": [],
    "suggested_adjustments": [],
    "global_rating_suggestion": 4.2,
    "confidence": 0.9,
    "explanation": "Les notes partielles sont cohérentes avec le verbatim positif"
}}
"""

# Prompt pour l'amélioration et suggestion de titre
TITLE_GENERATION_PROMPT = """
Tu es un expert en communication pour les avis patients d'établissements de santé.

Basé sur cette analyse complète, génère un titre accrocheur et représentatif:

Analyse sentiment: {sentiment_analysis}
Note calculée: {rating}/5
Verbatim: "{text}"

Critères pour le titre:
- Maximum 60 caractères
- Refléter le sentiment général
- Être respectueux et professionnel
- Éviter les superlatifs excessifs
- Mentionner l'aspect principal (soins, accueil, organisation, etc.)

Exemples de bons titres:
- "Excellent suivi médical, personnel à l'écoute"
- "Séjour correct mais attente aux urgences"
- "Déçu par l'organisation, bons soins"

Réponds UNIQUEMENT au format JSON:
{{
    "suggested_title": "Titre suggéré ici",
    "alternative_titles": ["Titre alternatif 1", "Titre alternatif 2"],
    "main_theme": "soins|accueil|organisation|hotellerie",
    "confidence": 0.8
}}
""" 