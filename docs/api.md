# Documentation de l'API

## 🔍 Vue d'ensemble

L'API du projet Mystères de l'UNIL 2025 est construite avec FastAPI et suit les principes REST. Elle fournit des endpoints pour :
- La gestion des chatbots
- La gestion des sessions de chat
- Le système de scoring
- La modération des contenus

## 🛣️ Endpoints

### Chatbots

#### GET /api/v1/bots
Liste tous les chatbots disponibles.

#### POST /api/v1/bots
Crée un nouveau chatbot.

#### GET /api/v1/bots/{bot_id}
Récupère les détails d'un chatbot spécifique.

### Chat

#### WebSocket /ws/chat/{session_id}
Point de connexion WebSocket pour les sessions de chat.

### Scores

#### GET /api/v1/scores
Récupère le tableau des scores.

#### POST /api/v1/scores
Enregistre un nouveau score.

## 🔒 Authentification

L'API utilise une authentification simple pour les classes participantes.

## 📝 Formats de données

### Bot
```json
{
  "id": "string",
  "name": "string",
  "instructions": "string",
  "created_at": "datetime",
  "class_id": "string"
}
```

### Score
```json
{
  "id": "string",
  "bot_id": "string",
  "player_id": "string",
  "score": "integer",
  "is_human": "boolean",
  "timestamp": "datetime"
}
```

## ⚡ WebSocket

Le protocole WebSocket est utilisé pour :
- Communication en temps réel pendant les sessions de chat
- Gestion de la file d'attente
- Notifications en direct

## 🚦 Limites et quotas

- Rate limiting : 100 requêtes/minute par IP
- Taille maximale des messages : 1000 caractères
- Connexions WebSocket simultanées : 1000 