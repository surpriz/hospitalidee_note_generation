# 📋 Guide des Questions Fermées - Hospitalidée

## 🎯 Nouveau Workflow de Validation

L'étape 4 "Validation" dispose maintenant de **deux onglets** pour offrir plus de contrôle sur la notation :

### 🎯 Onglet "Ajustement Rapide"
- **Fonctionnalité** : Interface originale d'ajustement simple
- **Usage** : Modification rapide de la note IA avec un slider
- **Avantage** : Rapidité pour des ajustements mineurs

### 📋 Onglet "Évaluation Détaillée" 
- **Fonctionnalité** : **NOUVELLES** questions fermées structurées
- **Usage** : Évaluation granulaire par catégories spécifiques
- **Avantage** : Contrôle précis et objectif

---

## 🏥 Questions Fermées : Établissement

**5 aspects évalués sur une échelle de 1 à 5 :**

1. **Votre relation avec les médecins**
   - Qualité de la communication et des interactions

2. **Votre relation avec le personnel**
   - Interactions avec infirmières, aides-soignants, etc.

3. **L'accueil**
   - Qualité de l'accueil à l'arrivée

4. **La prise en charge jusqu'à la sortie**
   - Suivi médical du début à la fin du séjour

5. **Les chambres et les repas**
   - Qualité de l'hébergement et de la restauration

---

## 👨‍⚕️ Questions Fermées : Médecins

**4 aspects évalués avec des choix prédéfinis :**

1. **Qualité des explications**
   - Options : Très insuffisantes → Excellentes

2. **Sentiment de confiance**
   - Options : Aucune confiance → Confiance totale

3. **Motivation à respecter la prescription**
   - Options : Aucune motivation → Très motivé

4. **Respect de votre identité, préférences et besoins**
   - Options : Pas du tout → Très respectueux

---

## 🔢 Calcul de la Note Finale Composite

La note finale est calculée selon une **moyenne pondérée** :

```
Note Finale = (40% × Note IA) + (30% × Ajustement Rapide) + (30% × Questions Fermées)
```

### Détail des Composantes

1. **Note IA (40%)** : Analyse automatique Mistral AI
2. **Ajustement Rapide (30%)** : Modification manuelle du slider
3. **Questions Fermées (30%)** : Moyenne des évaluations détaillées

### Calcul Questions Fermées
```
Questions Fermées = (Note Établissement + Note Médecins) / 2

Note Établissement = Moyenne des 5 aspects (1-5)
Note Médecins = Moyenne des 4 aspects convertis (1-5)
```

---

## 📊 Affichage des Résultats

### Étape 4 : Comparaison en Temps Réel
- Visualisation des 3 approches côte à côte
- Métriques avec deltas par rapport à la note IA
- Choix de l'approche préférée

### Étape 5 : Résultat Final Détaillé
- **Note composite finale** avec méthode de calcul
- **Détail de composition** : pourcentages de chaque approche
- **Évaluations spécifiques** dans des expandeurs :
  - 🏥 Détail Établissement (avec étoiles par aspect)
  - 👨‍⚕️ Détail Médecins (avec évaluations et notes converties)

---

## 💾 Export JSON Enrichi

Le fichier d'export inclut désormais :

```json
{
  "avis_text": "...",
  "final_rating": 4.2,
  "composite_calculation": {
    "ai_rating": 4.5,
    "quick_rating": 4.0,
    "detailed_rating": 4.1,
    "final_composite": 4.2,
    "weights": {"ai": 0.4, "quick": 0.3, "detailed": 0.3}
  },
  "detailed_evaluations": {
    "etablissement": {
      "note_globale": 4.2,
      "relation_medecins": 4,
      "relation_personnel": 5,
      "accueil": 4,
      "prise_en_charge": 4,
      "chambres_repas": 4
    },
    "medecins": {
      "note_globale": 4.0,
      "qualite_explications": {
        "evaluation": "Bonnes",
        "note": 4.0
      },
      "sentiment_confiance": {
        "evaluation": "Bonne confiance", 
        "note": 4.0
      }
      // ... autres aspects
    }
  }
}
```

---

## 🚀 Avantages du Nouveau Système

### Pour le Client
- ✅ **Contrôle granulaire** sur chaque aspect
- ✅ **Transparence** du calcul de la note finale
- ✅ **Flexibilité** : choix entre ajustement rapide ou détaillé
- ✅ **Objectivité** via questions standardisées

### Pour Hospitalidée
- ✅ **Données structurées** pour l'analyse
- ✅ **Réduction des biais** subjectifs
- ✅ **Amélioration continue** de l'algorithme IA
- ✅ **Conformité** aux standards d'évaluation médicale

### Respect des Cursor Rules
- ✅ **IA franco-française** : Mistral AI conservé (40%)
- ✅ **Performance** : < 3 secondes par analyse
- ✅ **Précision** : Amélioration de la fiabilité des notes
- ✅ **RGPD** : Pas de données personnelles stockées

---

## 🔧 Utilisation Pratique

1. **Étapes 1-3** : Inchangées (Saisie → Analyse → Proposition)
2. **Étape 4** : Choisir entre les deux onglets selon le besoin
3. **Étape 5** : Consulter le détail complet et exporter

**Recommandation** : Utiliser l'onglet "Évaluation Détaillée" pour des avis importants ou complexes, l'onglet "Ajustement Rapide" pour des modifications mineures. 