import os
import time
import codecs
import sqlite3
from aqt import mw
from aqt.qt import QAction, qconnect
from aqt.utils import askUser, showInfo, showCritical

from .edn_menu.shared_menu import register_module, register_action, should_initialize_module

def migrate_nids():
    addon_path = os.path.dirname(__file__)
    mapping_file = os.path.join(addon_path, "nid_mapping.txt")
    log_file = os.path.join(addon_path, "migration_debug.log")

    if not os.path.exists(mapping_file):
        showCritical(f"Le fichier d'identité est introuvable:\n{mapping_file}")
        return

    if not askUser(
        "Cette manipulation va relier vos cartes à la version de l'administrateur.\n\n"
        "Avez-vous fait une sauvegarde ?\nVoulez-vous lancer la mise à jour ?",
        title="Migration des cartes Anki EDN"
    ):
        return

    mw.progress.start(immediate=True)
    mw.checkpoint("Mise à jour NIDs")

    updated, not_found, conflicts, already_correct = 0, 0, 0, 0

    with open(log_file, "w", encoding="utf-8") as log:
        try:
            # --- INFO GÉNÉRALE ---
            db_path = mw.col.path
            log.write(f"=== MIGRATION DEBUG ===\n")
            log.write(f"Timestamp : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"DB path   : {db_path}\n")
            log.write(f"Mapping   : {mapping_file}\n\n")

            # --- LECTURE MAPPING ---
            with codecs.open(mapping_file, "r", "utf-8") as f:
                lines = f.readlines()
            log.write(f"Lignes dans le fichier mapping : {len(lines)}\n\n")

            mw.col.db.execute("PRAGMA foreign_keys = OFF")

            sample_updated = []
            sample_not_found = []
            sample_conflict = []

            for line in lines:
                line = line.strip()
                if not line or ',' not in line:
                    continue

                parts = line.split(',')
                guid = parts[0]
                try:
                    admin_nid = int(parts[1])
                except ValueError:
                    continue

                # Chercher la note par GUID
                local_nid = mw.col.db.scalar("SELECT id FROM notes WHERE guid = ?", guid)

                if local_nid:
                    if local_nid != admin_nid:
                        conflict = mw.col.db.scalar("SELECT id FROM notes WHERE id = ?", admin_nid)
                        if not conflict:
                            now = int(time.time())
                            mw.col.db.execute("UPDATE notes SET id = ?, mod = ?, usn = -1 WHERE id = ?", admin_nid, now, local_nid)
                            mw.col.db.execute("UPDATE cards SET nid = ?, mod = ?, usn = -1 WHERE nid = ?", admin_nid, now, local_nid)
                            updated += 1
                            if len(sample_updated) < 10:
                                sample_updated.append(f"  GUID={guid} | local_nid={local_nid} -> admin_nid={admin_nid}")
                        else:
                            conflicts += 1
                            if len(sample_conflict) < 5:
                                sample_conflict.append(f"  GUID={guid} | local_nid={local_nid} | admin_nid={admin_nid} (CONFLIT avec une autre note à cet ID)")
                    else:
                        already_correct += 1
                else:
                    not_found += 1
                    if len(sample_not_found) < 5:
                        sample_not_found.append(f"  GUID={guid} | admin_nid={admin_nid} (non trouvé localement)")

            # --- FORCE COMMIT via sqlite3 direct ---
            log.write(f"\n=== RÉSULTATS AVANT SAVE ===\n")
            log.write(f"  updated        : {updated}\n")
            log.write(f"  already_correct: {already_correct}\n")
            log.write(f"  not_found      : {not_found}\n")
            log.write(f"  conflicts      : {conflicts}\n\n")

            if sample_updated:
                log.write("Exemples de mises à jour effectuées :\n")
                log.write("\n".join(sample_updated) + "\n\n")
            if sample_not_found:
                log.write("Exemples de GUIDs non trouvés :\n")
                log.write("\n".join(sample_not_found) + "\n\n")
            if sample_conflict:
                log.write("Exemples de conflits :\n")
                log.write("\n".join(sample_conflict) + "\n\n")

            # Vérification POST-update : est-ce que l'ID est bien là en DB ?
            if sample_updated:
                log.write("=== VÉRIFICATION POST-UPDATE (lecture directe) ===\n")
                for entry in sample_updated[:3]:
                    # Extraire l'admin_nid de la ligne de log
                    admin_nid_check = int(entry.split("admin_nid=")[1])
                    row = mw.col.db.all("SELECT id, guid, mod, usn FROM notes WHERE id = ?", admin_nid_check)
                    log.write(f"  SELECT id={admin_nid_check} -> {row}\n")

            # Force save Anki
            mw.col.setMod()
            mw.col.save()

            log.write("\n=== SAVE TERMINÉ ===\n")
            log.write("col.setMod() et col.save() exécutés.\n")


        except Exception as e:
            if mw.progress:
                mw.progress.finish()
            log.write(f"\n!!! EXCEPTION : {e}\n")
            import traceback
            log.write(traceback.format_exc())
            showCritical(f"Une erreur est survenue lors de la migration :\n{str(e)}")
        finally:
            if mw.progress:
                mw.progress.finish()
            mw.reset()

    msg = (
        f"Migration terminée !\n\n"
        f"✅ Mis à jour : {updated}\n"
        f"🆗 Déjà corrects : {already_correct}\n"
        f"❌ GUIDs non trouvés : {not_found}\n"
    )
    if conflicts > 0:
        msg += f"⚠️ Conflits : {conflicts}\n"

    msg += f"\n📋 Un fichier de log a été créé pour diagnostic :\n{log_file}"

    showInfo(msg, title="Résultat de la migration")

    # Vérification DB et Synchronisation complète uniquement si des modifs ont été faites
    if updated > 0:
        if hasattr(mw.col, "modSchema"):
            mw.col.modSchema(check=True)
        mw.onCheckDB()
        mw.onSync()


def init_addon():
    # Ajout d'une option dans le menu 'Outils'
    register_module("anki_edn_nid", "Anki EDN - nid", "Migration de notes")

    if should_initialize_module("anki_edn_nid"):
        register_action("anki_edn_nid", "🛠️ Anki EDN - nid (Migration)", migrate_nids)

from aqt import gui_hooks
gui_hooks.profile_did_open.append(init_addon)
