# Guide des Workflows Séparés - Hospitalidée

## 🎯 Vue d'ensemble

L'application Hospitalidée propose désormais **deux workflows complètement séparés** pour répondre aux besoins spécifiques d'évaluation :

1. **🏥 Workflow Établissement** - Évaluation globale d'un établissement de santé
2. **👨‍⚕️ Workflow Médecin** - Évaluation spécifique d'un médecin

## 🚀 Lancement de l'application

```bash
cd hospitalidee_notation
python run_streamlit.py
```

L'application démarre sur : http://localhost:8501

## 📋 Workflow Établissement

### 🎯 Objectif
Évaluer l'expérience complète dans un établissement de santé (hôpital, clinique, etc.).

### 📝 Étape 1 : Questionnaire Établissement
**5 aspects évalués sur une échelle de 1 à 5 :**
- **Votre relation avec les médecins** - Communication et interactions
- **Votre relation avec le personnel** - Infirmières, aides-soignants
- **L'accueil** - Qualité de l'accueil à l'arrivée
- **La prise en charge jusqu'à la sortie** - Suivi médical complet
- **Les chambres et les repas** - Confort et restauration

**Calcul :** Note Établissement = Moyenne des 5 aspects

### 📝 Étape 2 : Saisie d'avis Établissement
- Zone de texte adaptée aux avis établissement
- Placeholder : "Décrivez votre expérience dans l'établissement : accueil, soins reçus, personnel, confort, locaux..."
- Analyse en temps réel du sentiment
- Cohérence avec le questionnaire

### ⭐ Étape 3 : Note IA Hybride Établissement
- Calcul intelligent combinant questionnaire + analyse textuelle
- Affichage spécialisé avec couleurs établissement (bleu)
- Comparaison questionnaire vs IA
- Facteurs de pondération adaptés

### 🔍 Étape 4 : Analyse Hybride Établissement
- **Colonne gauche :** Détail du questionnaire établissement uniquement
- **Colonne droite :** Analyse textuelle
- Synthèse de cohérence
- Répartition des sources

### 🎉 Étape 5 : Résultat Final Établissement
- Note finale hybride établissement
- Export JSON avec métadonnées établissement
- Workflow type : "etablissement"

## 👨‍⚕️ Workflow Médecin

### 🎯 Objectif
Évaluer spécifiquement la relation avec un médecin.

### 📝 Étape 1 : Questionnaire Médecin
**4 critères évalués avec select-slider :**
- **Qualité des explications** - Très insuffisantes → Excellentes
- **Sentiment de confiance** - Aucune confiance → Confiance totale
- **Motivation à respecter la prescription** - Aucune motivation → Très motivé
- **Respect de votre identité, préférences et besoins** - Pas du tout → Très respectueux

**Calcul :** Note Médecin = Moyenne des 4 critères (conversion texte → note)

### 📝 Étape 2 : Saisie d'avis Médecin
- Zone de texte adaptée aux avis médecin
- Placeholder : "Décrivez votre relation avec le médecin : communication, écoute, explications, traitement..."
- Analyse en temps réel du sentiment
- Cohérence avec le questionnaire

### ⭐ Étape 3 : Note IA Hybride Médecin
- Calcul intelligent combinant questionnaire + analyse textuelle
- Affichage spécialisé avec couleurs médecin (violet)
- Comparaison questionnaire vs IA
- Facteurs de pondération adaptés

### 🔍 Étape 4 : Analyse Hybride Médecin
- **Colonne gauche :** Détail du questionnaire médecin uniquement
- **Colonne droite :** Analyse textuelle
- Synthèse de cohérence
- Répartition des sources

### 🎉 Étape 5 : Résultat Final Médecin
- Note finale hybride médecin
- Export JSON avec métadonnées médecin
- Workflow type : "medecin"

## ⚡ Fonctionnalités Communes

### 🎯 Sélection du Type (Étape 0)
- Interface de choix entre les deux workflows
- Descriptions claires des spécificités
- Boutons d'accès directs

### 🔄 Navigation
- Sidebar adaptée selon le type sélectionné
- Icônes spécifiques (🏥 ou 👨‍⚕️)
- Progress tracking par workflow
- Bouton "Changer de type" disponible

### 🧠 IA Hybride
- **Mistral AI** pour l'analyse textuelle
- Combinaison intelligente questionnaire + sentiment
- Facteurs de pondération adaptés :
  - Questionnaire : 40%
  - Sentiment textuel : 30%
  - Intensité émotionnelle : 20%
  - Richesse du contenu : 10%

### 💾 Export & Reset
- Export JSON complet avec métadonnées workflow
- Bouton "Nouvelle analyse" retournant à la sélection
- Reset complet des données entre workflows

## 🔧 Architecture Technique

### 📁 Structure Modifiée
```
streamlit_apps/
├── besoin_1_notation_auto.py    # Application principale modifiée
└── ...

# Nouvelles fonctions ajoutées :
- step_0_selection_type()         # Sélection du workflow
- Adaptation des steps 1-5        # Logique séparée par type
- render_sidebar()                # Sidebar adaptée
- main()                          # Routage mis à jour
```

### 🔧 Variables Session State
```python
# Nouvelle variable clé
st.session_state.evaluation_type  # "etablissement" ou "medecin"

# Variables spécialisées
st.session_state.note_etablissement  # Note établissement (5 aspects)
st.session_state.note_medecins       # Note médecin (4 critères)
st.session_state.note_questions_fermees  # Note finale du questionnaire selon le type
```

### 🎨 Interface Adaptée
- **Couleurs :** Bleu pour établissement, violet pour médecin
- **Icônes :** 🏥 pour établissement, 👨‍⚕️ pour médecin
- **Textes :** Personnalisés selon le contexte
- **Placeholders :** Adaptés au type d'évaluation

## ✅ Avantages de la Séparation

### 🎯 Spécialisation
- Questionnaires adaptés aux besoins spécifiques
- Analyses centrées sur le bon contexte
- Évite la confusion entre les évaluations

### 🚀 Performance
- Workflows optimisés pour chaque cas d'usage
- Interface simplifiée et ciblée
- Temps de saisie réduit

### 📊 Données de Qualité
- Évaluations plus précises
- Cohérence améliorée
- Analytics séparés possible

### 🔄 Flexibilité
- Évolutions indépendantes des workflows
- Ajout facile de nouveaux types
- Personnalisation avancée

## 🧪 Tests

### Script de Test Automatisé
```bash
python test_workflows_separes.py
```

**Tests inclus :**
- ✅ Workflow Établissement complet
- ✅ Workflow Médecin complet  
- ✅ Séparation et indépendance
- ✅ Calculs IA hybrides
- ✅ Gestion des erreurs

### Test Manuel
1. Lancer l'application
2. Tester workflow Établissement de A à Z
3. Utiliser "Nouvelle analyse"
4. Tester workflow Médecin de A à Z
5. Vérifier la séparation des données

## 🎉 Conclusion

Les workflows séparés offrent une expérience utilisateur optimisée et des évaluations plus précises. Chaque type d'évaluation dispose maintenant de son propre parcours spécialisé, tout en conservant la puissance de l'IA hybride Mistral pour l'analyse textuelle.

**Prochaines étapes possibles :**
- Ajout d'autres types d'évaluation (service spécifique, urgences, etc.)
- Analytics séparés par workflow
- Personnalisation avancée des questionnaires
- Export vers différents formats selon le type 