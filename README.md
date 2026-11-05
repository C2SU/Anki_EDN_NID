# Anki EDN - Synchronisation des NID

Realignez les identifiants uniques de vos notes EDN en un clic pour garantir la coherence de vos liaisons et de vos liens.

Dans le cadre du cursus EDN / ECNi, les paquets officiels et collaboratifs reposent sur des identifiants administratifs stables (NID). Cet add-on permet d'harmoniser les NID de votre collection locale avec la reference officielle sans alterer votre progression ni vos historiques d'apprentissage.

---

## Quand et Comment Utiliser cet Add-on ?

| Etape | Intitule | Action a realiser |
| :--- | :--- | :--- |
| **Etape 1** | **Declenchement Securise** | Apres l'installation et le redemarrage d'Anki, rendez-vous dans le menu superieur : `Anki EDN > Reparer les NID`. |
| **Etape 2** | **Rapport de Conformite** | L'outil scanne votre collection, applique les alignements requis et affiche un bilan transparent : nombre de notes mises a jour, deja conformes ou ecarts eventuels. |

---

## Garanties de Securite

- **Integrite absolue de la progression** : La modification d'un NID administrativement remappe ne reinitialise jamais les intervalles FSRS / SM-2, ni les dates de revue, ni les historiques d'etude.
- **Journal d'audit detaille** : Chaque operation est consignee ligne par ligne dans `migration_debug.log` a la racine du dossier de l'add-on.
- **Detection proactive des conflits** : Si un identifiant cible est deja attribue a une note locale differente, l'operation est isolee et signalee sans ecrasement sauvage.

---

## Format du Fichier de Mapping (`nid_mapping.txt`)

Si vous etes administrateur de deck ou tuteur et souhaitez generer un plan d'alignement pour votre promotion, placez un fichier `nid_mapping.txt` a la racine de l'add-on :

```text
GUID_ORIGINE,NID_CIBLE
abc123def456,1652841200001
xyz789uva345,1652841200002
```

Les lignes vides ou mal formatees sont automatiquement ignorees.

---

## Installation

### Via AnkiWeb (Recommande)
1. Dans Anki, ouvrez le menu `Outils > Modules complementaires > Acquerir des modules complementaires...`
2. Saisissez le code : **2135076010**
3. Redemarrez Anki.

### Depuis le fichier .ankiaddon
1. Telechargez le fichier `.ankiaddon` depuis les releases locales ou GitHub.
2. Dans Anki, ouvrez `Outils > Modules complementaires > Installer depuis un fichier...`
3. Selectionnez le package et redemarrez Anki.

---

## Assistance et Documentation

- Code d'installation AnkiWeb : **2135076010**
- Documentation officielle EDN : [Portail Anki EDN](https://c2su.github.io/Anki_EDN/Anki_EDN.html)
- Communaute d'entraide : [Serveur Discord EDN](https://discord.gg/2A7zHAEBYt)
- Code source : [Depot GitHub C2SU/Anki_EDN_NID](https://github.com/C2SU/Anki_EDN_NID)
- Integration : Fait partie integrante de la suite logicielle Anki EDN
