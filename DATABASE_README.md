# HttpPro - Enhanced TLS Error Management with Database

## 🚀 Nouvelles Fonctionnalités

### Base de Données SQLite

Les domaines ignorés sont maintenant stockés dans une base de données SQLite (`ignore_hosts.db`) avec les informations suivantes :

- **Date d'ajout** : Quand le domaine a été ajouté
- **Origine** : Pourquoi le domaine a été ajouté (ex: `tls_error`, `manual`, `file_import`)
- **Compteur** : Nombre de fois où le domaine a été rencontré
- **Statut** : Actif ou inactif
- **Dernière occurrence** : Dernière fois où le domaine a été vu

### Types d'Origine

- `existing_file` : Domaine importé depuis un fichier ignore-host.txt existant
- `file_import` : Domaine importé depuis un fichier via l'utilitaire
- `tcp_tls_error` : Erreur TLS détectée dans tcp_end
- `client_tls_error` : Erreur TLS détectée dans tls_failed_client
- `manual` : Ajouté manuellement via l'utilitaire
- `manual_test` : Domaine de test ajouté manuellement

## 📋 Utilisation de l'Utilitaire de Gestion

### Commandes Disponibles

#### Lister les domaines

```bash
python manage_db.py list                    # Domaines actifs seulement
python manage_db.py list --all             # Tous les domaines (actifs + inactifs)
```

#### Ajouter un domaine

```bash
python manage_db.py add "example.com"                      # Origine: manual
python manage_db.py add "example.com" --origin "custom"    # Origine personnalisée
```

#### Rechercher un domaine

```bash
python manage_db.py search "graph.facebook.com"
```

#### Statistiques

```bash
python manage_db.py stats
```

#### Import/Export

```bash
python manage_db.py import fichier.txt --origin "bulk_import"
python manage_db.py export output.txt
```

#### Désactiver un domaine

```bash
python manage_db.py remove "example.com"
```

## 🛠️ Architecture

### Flux de Données

1. **Au démarrage** : Le plugin TLS importe automatiquement les domaines du fichier `ignore-host.txt`
2. **Pendant l'exécution** : Les nouvelles erreurs TLS sont automatiquement ajoutées à la DB
3. **Compatibilité** : Le fichier `ignore-host.txt` est maintenu à jour pour compatibilité

### Fichiers Principaux

- `core/database.py` : Gestionnaire de base de données SQLite
- `plugins/tls.py` : Plugin TLS mis à jour pour utiliser la DB
- `manage_db.py` : Utilitaire en ligne de commande
- `ignore_hosts.db` : Base de données SQLite (créée automatiquement)

## 🔧 Exemples d'Utilisation

### Voir l'historique d'un domaine

```bash
python manage_db.py search "i.instagram.com"
```

Résultat :

```
🔍 Domain Information:
   Domain: i.instagram.com
   Origin: existing_file
   Status: Active
   Date Added: 2025-07-06 18:53:31
   Last Seen: 2025-07-06 18:53:31
   Count: 1
```

### Voir les statistiques par origine

```bash
python manage_db.py stats
```

Résultat :

```
📊 Database Statistics:
   Total domains: 62
   Active domains: 62
   Inactive domains: 0
🎯 Domains by origin:
   existing_file: 57
   file_import: 4
   manual_test: 1
```

## 🛡️ Fonctionnement du Proxy

Le proxy fonctionne exactement comme avant mais avec des améliorations :

- **Préservation** de la configuration `--ignore-hosts` en ligne de commande
- **Ajout automatique** des nouveaux domaines avec erreurs TLS
- **Traçabilité complète** de tous les domaines ignorés
- **Gestion par origine** pour comprendre pourquoi chaque domaine est ignoré

## 🗄️ Structure de la Base de Données

```sql
CREATE TABLE ignore_hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT UNIQUE NOT NULL,
    origin TEXT NOT NULL,
    date_added TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    count INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT 1
);
```

## 📈 Avantages

1. **Traçabilité** : Savoir quand et pourquoi chaque domaine a été ajouté
2. **Statistiques** : Comprendre les patterns d'erreurs TLS
3. **Gestion fine** : Pouvoir désactiver des domaines spécifiques
4. **Historique** : Garder une trace des domaines même désactivés
5. **Performance** : Requêtes SQL rapides pour des milliers de domaines
6. **Compatibilité** : Maintien du fichier texte pour la compatibilité

Ce système offre une gestion professionnelle des domaines ignorés tout en conservant la simplicité d'utilisation.
