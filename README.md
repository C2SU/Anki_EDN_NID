# Anki EDN - NID Migration

## 📋 Description

**Anki EDN NID** est un addon Anki qui permet de les identifiants de notes (NID) pour mieux profiter de [Anki EDN](https://tools.c2su.org/Anki_EDN/book.html). 
Cet addon est conçu pour les environnements d'apprentissage collaboratifs où plusieurs utilisateurs doivent maintenir une cohérence dans les identifiants de leurs cartes Anki.

## 🎯 Fonctionnalité

L'addon fournit un outil de migration qui :

- **Utilise un fichier de mapping** : Lit un fichier `nid_mapping.txt` contenant la correspondance GUID → NID administrateur
- **Gère les conflits** : Identifie et rapporte les conflits d'identifiants
- **Génère des logs détaillés** : Crée un fichier de debug pour suivre tous les changements effectués

## 🚀 Utilisation

### 1. Préparation du fichier de mapping

Créez un fichier `nid_mapping.txt` dans le répertoire de l'addon avec le format suivant :

```
GUID1,NID_ADMIN_1
GUID2,NID_ADMIN_2
GUID3,NID_ADMIN_3
```

Exemple :

```
abc123def456,1652841200001
xyz789uva345,1652841200002
```
Automatisable dans la console de debugging anki.

### 2. Résultats et logs

À la fin de la migration, vous verrez :

- ✅ **Mis à jour** : nombre de notes dont le NID a été changé
- 🆗 **Déjà corrects** : nombre de notes ayant déjà le bon NID
- ❌ **GUIDs non trouvés** : nombre de GUIDs du fichier mapping introuvables dans votre collection
- ⚠️ **Conflits** : nombre de conflits détectés (NID de destination déjà occupé)

Un fichier `migration_debug.log` est créé dans le répertoire de l'addon avec tous les détails.

## 📁 Structure du fichier mapping

Le fichier `nid_mapping.txt` doit être placé dans le répertoire de l'addon et contenir :

- **Une entrée par ligne**
- **Format** : `GUID,NID_ADMIN`
- Les lignes vides et mal formatées sont ignorées

## 📝 Version

- **Version** : 1.0.0
- **Package** : EDN_sync_NID

## 🔗 Intégration EDN

Cet addon fait partie de l'écosystème **Anki EDN** et s'intègre avec le système de menu EDN pour une meilleure organisation des addons.

---

**Besoin d'aide ?** Consultez le fichier log `migration_debug.log` généré après chaque migration pour diagnostiquer les problèmes.

## 💡 Support

Pour toute question, suggestion ou rapport de bug :
- [Anki EDN](https://tools.c2su.org/Anki_EDN/book/)
- [Discord Anki EDN](https://discord.gg/2A7zHAEBYt)
- [GitHub](https://github.com/C2SU/Anki_EDN_NID)
- [AnkiWeb](https://ankiweb.net/shared/info/445658251)