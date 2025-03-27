# Guide de déploiement

## 🌍 Environnement de production

### Prérequis

- Python 3.11.8
- Redis
- Serveur NGINX
- Supervisord
- Base de données SQLite

### Configuration système

```bash
# Installation des dépendances système
sudo apt update
sudo apt install -y python3.11 python3.11-venv redis-server nginx supervisor

# Configuration de Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 🚀 Déploiement

### 1. Préparation

```bash
# Cloner le dépôt
git clone [URL_DU_REPO]
cd mysteres-unil

# Installer Python 3.11.8
pyenv install 3.11.8
pyenv local 3.11.8

# Installer les dépendances
make install
```

### 2. Configuration

Créer le fichier `.env.prod` :

```env
DATABASE_URL=sqlite:///./prod.db
REDIS_URL=redis://localhost:6379
SECRET_KEY=votre-cle-secrete-production
ENVIRONMENT=production
```

### 3. Base de données

```bash
# Appliquer les migrations
make build
```

### 4. Configuration NGINX

Créer `/etc/nginx/sites-available/mysteres-unil` :

```nginx
server {
    listen 80;
    server_name mysteres.unil.ch;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /chemin/vers/mysteres-unil/src/frontend/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/mysteres-unil /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Configuration Supervisord

Créer `/etc/supervisor/conf.d/mysteres-unil.conf` :

```ini
[program:mysteres-unil]
command=/chemin/vers/poetry/bin/poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/chemin/vers/mysteres-unil
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/mysteres-unil/err.log
stdout_logfile=/var/log/mysteres-unil/out.log
environment=
    DATABASE_URL="sqlite:///./prod.db",
    REDIS_URL="redis://localhost:6379",
    SECRET_KEY="votre-cle-secrete-production",
    ENVIRONMENT="production"
```

```bash
# Créer les dossiers de logs
sudo mkdir -p /var/log/mysteres-unil
sudo chown -R www-data:www-data /var/log/mysteres-unil

# Recharger Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mysteres-unil
```

## 📊 Monitoring

### Logs

```bash
# Logs de l'application
tail -f /var/log/mysteres-unil/out.log
tail -f /var/log/mysteres-unil/err.log

# Logs NGINX
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Statut des services

```bash
# Vérifier l'état de l'application
sudo supervisorctl status mysteres-unil

# Vérifier l'état de Redis
sudo systemctl status redis-server

# Vérifier l'état de NGINX
sudo systemctl status nginx
```

## 🔄 Mise à jour

```bash
# Arrêter l'application
sudo supervisorctl stop mysteres-unil

# Mettre à jour le code
git pull origin main

# Installer les dépendances
make install

# Appliquer les migrations
make build

# Redémarrer l'application
sudo supervisorctl start mysteres-unil
```

## 🔧 Dépannage

### Problèmes courants

1. **L'application ne démarre pas**
   - Vérifier les logs Supervisor
   - Vérifier les permissions des fichiers
   - Vérifier la configuration .env

2. **Erreurs WebSocket**
   - Vérifier la configuration NGINX
   - Vérifier les paramètres du pare-feu
   - Vérifier la connexion Redis

3. **Problèmes de base de données**
   - Vérifier les permissions du fichier SQLite
   - Vérifier l'état des migrations
   - Faire une sauvegarde si nécessaire 