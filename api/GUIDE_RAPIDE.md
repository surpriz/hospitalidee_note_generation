# 🚀 Hospitalidée IA API - Guide de Démarrage Rapide

**API REST prête à l'emploi pour vos développeurs !**

> 💡 **Ce guide** : Tests en local  
> 🌐 **Pour VPS** : Consultez `DEPLOIEMENT_VPS.md`

## ⚡ Installation en 3 étapes

### 1. Décompressez l'archive
```bash
unzip hospitalidee-ia-api.zip
cd hospitalidee-ia-api
```

### 2. Configurez votre clé API Mistral
```bash
cp config.env.example .env
nano .env  # Ajoutez votre MISTRAL_API_KEY
```

### 3. Démarrez l'API
```bash
./scripts/install.sh  # Installation automatique
# OU
docker-compose up -d  # Si Docker est installé
```

**🎉 C'est tout ! Votre API est prête sur http://localhost:8000**

## 🌐 Installation VPS (Production)

Pour mettre l'API en ligne sur votre serveur :

```bash
# 1. Transférez sur VPS
scp hospitalidee-ia-api.zip root@VOTRE_IP:/root/

# 2. Installez sur VPS  
ssh root@VOTRE_IP
cd /root && unzip hospitalidee-ia-api.zip
cd hospitalidee-ia-api && ./scripts/install.sh

# 3. Ouvrez le port
sudo ufw allow 8000/tcp

# 4. API accessible sur http://VOTRE_IP:8000
```

📖 **Guide détaillé** : `DEPLOIEMENT_VPS.md`

---

## 🎯 Un seul appel pour tout faire

```javascript
// Adaptez l'URL selon votre environnement :
// 'http://localhost:8000'     → Tests en local
// 'http://VOTRE_IP_VPS:8000'  → VPS production
const response = await fetch('http://localhost:8000/evaluate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        type_evaluation: "etablissement",
        avis_text: "Séjour excellent, personnel attentif...",
        questionnaire_etablissement: {
            medecins: 4, personnel: 5, accueil: 3,
            prise_en_charge: 4, confort: 3
        }
    })
});

const result = await response.json();
console.log(`Note: ${result.note_finale}/5`);  // Note: 4.2/5
```

---

## 📖 Accès direct

- **🎯 API :** http://localhost:8000/evaluate
- **📚 Documentation :** http://localhost:8000/docs
- **🏥 Health check :** http://localhost:8000/health

---

## 🔧 Commandes essentielles

```bash
# Démarrer
./scripts/start.sh

# Arrêter
./scripts/stop.sh

# Tester
./scripts/test.sh

# Voir les logs
docker-compose logs -f
```

---

## 🆘 En cas de problème

1. **API ne démarre pas :** Vérifiez votre clé Mistral dans `.env`
2. **Port occupé :** Changez `API_PORT=8001` dans `.env`
3. **Erreur Docker :** Installez Docker ou utilisez Python direct

**Support :** Consultez `README.md` pour la documentation complète

---

## ✅ Validation rapide

```bash
# Test que tout fonctionne
curl http://localhost:8000/health

# Test avec un avis
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "type_evaluation": "etablissement",
    "avis_text": "Personnel très gentil et professionnel",
    "questionnaire_etablissement": {
      "medecins": 4, "personnel": 5, "accueil": 3,
      "prise_en_charge": 4, "confort": 3
    }
  }'
```

**Réponse attendue :** Note entre 1 et 5 + sentiment + confiance

---

## 🏁 Prêt pour la production !

Votre API Hospitalidée IA est maintenant opérationnelle. Vos développeurs peuvent l'intégrer immédiatement dans votre site web.

**Besoin d'aide ?** → `README.md` ou http://localhost:8000/docs