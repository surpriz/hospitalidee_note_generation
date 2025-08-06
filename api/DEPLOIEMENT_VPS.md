# 🌐 Hospitalidée IA API - Déploiement VPS

**Guide complet pour installer l'API sur un VPS et y accéder depuis votre site web**

## 🎯 Objectif

Installer l'API Hospitalidée IA sur votre **VPS** pour qu'elle soit accessible depuis votre site web à une adresse comme :
- `https://votre-vps.com:8000/evaluate`
- `https://api.votre-site.com/evaluate`
- `http://IP.DU.VPS:8000/evaluate`

---

## 🚀 Installation sur VPS Ubuntu/Debian

### 1. Connexion au VPS
```bash
# Connectez-vous à votre VPS
ssh root@VOTRE_IP_VPS
# ou
ssh utilisateur@votre-domaine.com
```

### 2. Installation automatique
```bash
# Téléchargez l'API (exemple avec scp)
scp hospitalidee-ia-api.zip root@VOTRE_IP:/root/

# Sur le VPS, décompressez
cd /root
unzip hospitalidee-ia-api.zip
cd hospitalidee-ia-api

# Lancez l'installation automatique
chmod +x scripts/install.sh
./scripts/install.sh
```

### 3. Configuration pour accès externe
```bash
# Éditez la configuration
nano .env

# Modifiez ces lignes :
API_HOST=0.0.0.0          # Important : permet l'accès externe
API_PORT=8000             # Ou autre port de votre choix
CORS_ORIGINS=https://votre-site.com,https://www.votre-site.com
ENVIRONMENT=production
```

### 4. Ouverture du port (Firewall)
```bash
# Ubuntu/Debian avec ufw
sudo ufw allow 8000/tcp
sudo ufw reload

# CentOS/RHEL avec firewalld
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload

# Vérification
sudo ufw status
```

### 5. Démarrage de l'API
```bash
# Démarrage
./scripts/start.sh

# Vérification que ça fonctionne
curl http://localhost:8000/health

# Test depuis l'extérieur (remplacez par votre IP)
curl http://VOTRE_IP_VPS:8000/health
```

---

## 🌍 Accès depuis votre site web

### Remplacez localhost par votre VPS

**❌ Local (développement) :**
```javascript
fetch('http://localhost:8000/evaluate', {
```

**✅ VPS (production) :**
```javascript
fetch('http://VOTRE_IP_VPS:8000/evaluate', {
// ou
fetch('https://api.votre-site.com/evaluate', {
```

### Exemple complet avec IP VPS
```javascript
// Remplacez 192.168.1.100 par l'IP de votre VPS
const API_URL = 'http://192.168.1.100:8000';

const response = await fetch(`${API_URL}/evaluate`, {
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
console.log(`Note: ${result.note_finale}/5`);
```

---

## 🔒 Configuration HTTPS (Recommandée)

### Option 1: Reverse Proxy Nginx

```bash
# Installation Nginx
sudo apt update
sudo apt install nginx

# Configuration Nginx
sudo nano /etc/nginx/sites-available/hospitalidee-api
```

Contenu du fichier :
```nginx
server {
    listen 80;
    server_name api.votre-site.com;  # Remplacez par votre domaine
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activation
sudo ln -s /etc/nginx/sites-available/hospitalidee-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Votre API est maintenant accessible sur :
# http://api.votre-site.com/evaluate
```

### Option 2: Certificat SSL avec Let's Encrypt

```bash
# Installation Certbot
sudo apt install certbot python3-certbot-nginx

# Génération certificat SSL
sudo certbot --nginx -d api.votre-site.com

# Votre API devient accessible en HTTPS :
# https://api.votre-site.com/evaluate
```

---

## 🔧 Configuration Production

### Variables d'environnement VPS
```bash
# .env pour production VPS
MISTRAL_API_KEY=your_real_mistral_key
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
DEBUG_MODE=false
CORS_ORIGINS=https://votre-site.com,https://www.votre-site.com
LOG_LEVEL=INFO
```

### Démarrage automatique au boot
```bash
# Créer un service systemd
sudo nano /etc/systemd/system/hospitalidee-api.service
```

Contenu :
```ini
[Unit]
Description=Hospitalidee IA API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/hospitalidee-ia-api
ExecStart=/usr/bin/docker-compose up
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activation du service
sudo systemctl enable hospitalidee-api
sudo systemctl start hospitalidee-api

# L'API démarre automatiquement au redémarrage du VPS
```

---

## 🧪 Tests depuis votre site web

### Test de connexion
```javascript
// Test rapide dans la console de votre site
fetch('http://VOTRE_IP_VPS:8000/health')
  .then(r => r.json())
  .then(data => console.log('API Status:', data.status))
  .catch(e => console.error('API inaccessible:', e));
```

### Test complet d'évaluation
```javascript
// Test avec un vrai avis
fetch('http://VOTRE_IP_VPS:8000/evaluate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        type_evaluation: "etablissement",
        avis_text: "Test depuis le site web - personnel très gentil",
        questionnaire_etablissement: {
            medecins: 4, personnel: 5, accueil: 3,
            prise_en_charge: 4, confort: 3
        }
    })
})
.then(r => r.json())
.then(data => {
    console.log('✅ API fonctionne !');
    console.log('Note:', data.note_finale + '/5');
    console.log('Sentiment:', data.sentiment);
})
.catch(e => console.error('❌ Erreur API:', e));
```

---

## 🚨 Résolution de problèmes VPS

### API non accessible depuis l'extérieur

**1. Vérifiez le firewall :**
```bash
sudo ufw status
sudo ufw allow 8000/tcp
```

**2. Vérifiez que l'API écoute sur 0.0.0.0 :**
```bash
# Dans .env
API_HOST=0.0.0.0  # Pas 127.0.0.1 !

# Redémarrez
./scripts/stop.sh
./scripts/start.sh
```

**3. Vérifiez que le port est ouvert :**
```bash
sudo netstat -tlnp | grep 8000
# Doit afficher : 0.0.0.0:8000
```

### Erreurs CORS

**Dans .env :**
```bash
CORS_ORIGINS=https://votre-site.com,https://www.votre-site.com,http://votre-site.com
```

### Performance lente

**Optimisations VPS :**
```bash
# Dans .env
ENABLE_CACHE=true
REDIS_URL=redis://localhost:6379

# Décommentez Redis dans docker-compose.yml
# Redémarrez
docker-compose down
docker-compose up -d
```

---

## 📋 Checklist déploiement VPS

### Avant installation
- [ ] VPS avec Ubuntu/Debian 18.04+
- [ ] Accès SSH root ou sudo
- [ ] Docker installé (ou sera installé par le script)
- [ ] Port 8000 disponible
- [ ] Nom de domaine configuré (optionnel)

### Après installation
- [ ] API accessible sur `http://IP_VPS:8000/health`
- [ ] Test depuis votre site web OK
- [ ] CORS configuré pour votre domaine
- [ ] Firewall ouvert sur port 8000
- [ ] Certificat SSL configuré (recommandé)
- [ ] Démarrage automatique activé

### URLs finales
- [ ] `http://IP_VPS:8000/evaluate` → Endpoint principal
- [ ] `http://IP_VPS:8000/docs` → Documentation
- [ ] `http://IP_VPS:8000/health` → Status API

---

## 🎉 Résultat final

Votre API sera accessible à l'adresse :
- **Simple :** `http://VOTRE_IP_VPS:8000/evaluate`
- **Avec domaine :** `https://api.votre-site.com/evaluate`

Vos développeurs pourront l'appeler depuis votre site web exactement comme dans les exemples, en remplaçant simplement `localhost:8000` par votre vraie adresse VPS.

**🚀 Votre IA est maintenant en ligne et accessible depuis internet !**