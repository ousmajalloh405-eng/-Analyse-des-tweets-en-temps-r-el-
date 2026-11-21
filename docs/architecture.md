# Architecture
twitter/X API (optionnel) Simulateur
│ │
└──────┬───────────────┘
▼
run_producer.py
│ publish(tweets_raw)
▼
Apache Kafka ───► [topic tweets_raw]
│
▼
Spark Structured Streaming (local[*])

clean_text()

TextBlob → polarity / label
│ foreachBatch
▼
MongoDB (analyzed_tweets)
│
▼
Streamlit dashboard


## Choix techniques

| Composant | Rôle | Justification |
|---|---|---|
| Kafka (KRaft) | Buffer de streaming | Découplage producteur/consommateur, replay |
| Spark 3.5 Structured Streaming | Traitement temps réel | API DataFrame, `foreachBatch` vers Mongo |
| TextBlob | NLP de base | Simple, sans modèle lourd ; multilingue limité |
| MongoDB 7 | Stockage NoSQL | Documents JSON, souplesse de schéma, `_id` idempotent |
| Streamlit | Dashboard | Prototypage rapide, mise à jour auto |

## Modèle de document (analyzed_tweets)

```json
{
  "_id": "tweet_id",
  "tweet_id": "tweet_id",
  "text": "...",
  "cleaned_text": "...",
  "author_id": "...",
  "lang": "fr",
  "hashtags": "#data #spark",
  "source": "simulator|twitter",
  "created_at": "ISO-8601",
  "polarity": 0.5,
  "sentiment": "positive|negative|neutral"
}


---

## `README.md` (les 12 points exigés)

```markdown
# Projet 10 — Analyse des tweets en temps réel

Pipeline Data Engineering : collecte → Kafka → Spark Streaming → NLP → MongoDB → Dashboard.

## 1. Problème métier
Une entreprise veut suivre en direct la perception d'un sujet (marque, mot-clé, hashtag)
sur Twitter/X. Il faut collecter, analyser le sentiment et visualiser sans latence
significative, avec un historique exploitable.

## 2. Objectifs
- Ingérer des tweets en continu via Kafka.
- Analyser le sentiment en temps réel avec Spark Structured Streaming.
- Stocker les résultats dans MongoDB.
- Fournir un dashboard Streamlit rafraîchi automatiquement.
- Fonctionner **sans compte X** grâce à un simulateur qui utilise la même architecture.

## 3. Architecture globale
Voir `docs/architecture.md`.

## 4. Rôle de chaque technologie
| Techno | Rôle |
|---|---|
| Kafka | File de messages, découplage, replay |
| Spark Structured Streaming | Traitement temps réel, NLP |
| TextBlob | Analyse de sentiment (baseline) |
| MongoDB | Stockage NoSQL des tweets analysés |
| Streamlit | Dashboard temps réel |
| Docker Compose | Orchestration locale |
| Python 3.11 | Langage d'implémentation |

## 5. Fonctionnement du pipeline
1. `run_producer.py` publie dans `tweets_raw` (simulateur ou API X).
2. `stream_job.py` lit Kafka, nettoie le texte, calcule `polarity`/`sentiment`.
3. `write_batch()` insère dans `analyzed_tweets` (`_id = tweet_id`, idempotent).
4. `app.py` interroge Mongo et rafraîchit l'UI.

## 6. Installation
Prérequis : Docker + Docker Compose v2, Python 3.11 (optionnel hors Docker).
```bash
git clone <repo> && cd realtime-twitter-sentiment
cp .env.example .env
# éditer .env (mot de passe Mongo, mode producer)
docker compose up -d --build
make topics



---

## Ce qui est réellement testable (transparence)

| Élément | Statut |
|---|---|
| `pytest` sur `sentiment`, `simulator`, `settings` | ✅ Testable **chez toi** sans service (`pip install -r requirements.txt`) |
| `ruff check .` | ✅ Testable chez toi |
| `docker compose up` + `check_services.sh` | ⚠️ **Non testé ici** — à valider sur ta machine |
| Job Spark bout-en-bout vers Mongo | ⚠️ **Non testé ici** |
| Dashboard Streamlit affichant des données | ⚠️ **Non testé ici** |
| Appels réels API X | ❌ **Non testé** (compte + quotas requis) |

Je ne marque **rien** comme testé ici. Ce tableau est ta checklist de validation.

---

## Étapes manuelles finales (à faire de ton côté)

1. **Créer le dossier** et coller tous les fichiers des Livraisons 1, 2 et 3 en respectant l'arborescence.
2. **Installer** : `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` (ajoute `pydantic-settings==2.2.1`).
3. **Lancer les tests** : `pytest -q` et `ruff check .`. Corrige les éventuels échecs `test_positive`/`test_negative` (voir limite TextBlob).
4. **Docker** : `cp .env.example .env`, édite le mot de passe Mongo, puis `make up`, `make topics`, `bash scripts/check_services.sh`.
5. **Pipeline démo** : `python -m src.producer.run_producer` puis `python -m src.spark.stream_job` (dans deux terminaux). Vérifie Mongo et le dashboard.
6. **Packaging ZIP** : `make package` → `dist/realtime-twitter-sentiment.zip`. L'archive exclut `.env`, `.venv`, caches et secrets.
7. **GitHub** :
   ```bash
   git init && git add . && git commit -m "feat: realtime twitter sentiment pipeline"
   git branch -M main
   git remote add origin git@github.com:<toi>/realtime-twitter-sentiment.git
   git push -u origin main