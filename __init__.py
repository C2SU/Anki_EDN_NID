import os
import time
import codecs
from aqt import mw
from aqt.utils import showCritical, tooltip

# Imports are deferred to init_addon() to avoid early-loading issues

def migrate_nids():
    if not mw or not mw.col:
        return

    addon_path = os.path.dirname(__file__)
    mapping_file = os.path.join(addon_path, "nid_mapping.txt")

    if not os.path.exists(mapping_file):
        showCritical(f"Le fichier d'identité est introuvable :\n{mapping_file}")
        return

    mw.progress.start(immediate=True)
    mw.checkpoint("Mise à jour NIDs")

    updated = 0

    try:
        with codecs.open(mapping_file, "r", "utf-8") as f:
            lines = f.readlines()

        mw.col.db.execute("PRAGMA foreign_keys = OFF")

        local_notes = dict(mw.col.db.all("SELECT guid, id FROM notes"))
        existing_ids = set(local_notes.values())
        now = int(time.time())

        for line in lines:
            line = line.strip()
            if not line or "," not in line:
                continue

            guid, nid_str = line.rsplit(",", 1)
            try:
                admin_nid = int(nid_str)
            except ValueError:
                continue

            local_nid = local_notes.get(guid)
            if local_nid and local_nid != admin_nid:
                if admin_nid not in existing_ids:
                    mw.col.db.execute(
                        "UPDATE notes SET id = ?, mod = ?, usn = -1 WHERE id = ?",
                        admin_nid, now, local_nid
                    )
                    mw.col.db.execute(
                        "UPDATE cards SET nid = ?, mod = ?, usn = -1 WHERE nid = ?",
                        admin_nid, now, local_nid
                    )
                    existing_ids.discard(local_nid)
                    existing_ids.add(admin_nid)
                    local_notes[guid] = admin_nid
                    updated += 1

        if updated > 0:
            mw.col.setMod()
            mw.col.save()

    except Exception as e:
        if mw.progress:
            mw.progress.finish()
        showCritical(f"Une erreur est survenue lors de la migration :\n{str(e)}")
        return
    finally:
        if mw.progress:
            mw.progress.finish()
        mw.reset()

    if updated > 0:
        if hasattr(mw.col, "mod_schema"):
            mw.col.mod_schema(check=False)
        elif hasattr(mw.col, "modSchema"):
            mw.col.modSchema(check=False)
        tooltip(f"NIDs réparés ({updated} notes mises à jour).", period=3500)
        mw.onSync()
    else:
        tooltip("Tous les NIDs sont déjà à jour.", period=2500)


def init_addon():
    # Deferred import to ensure the package structure is fully recognized by Anki
    try:
        from .edn_menu.shared_menu import register_module, register_action, should_initialize_module
    except ImportError:
        # Fallback if the package is loaded in a way that relative imports fail
        from .edn_menu import register_module, register_action, should_initialize_module

    register_module("anki_edn_nid", "Anki EDN - nid", "Migration de notes")

    if should_initialize_module("anki_edn_nid"):
        register_action("anki_edn_nid", "Réparer les NID", migrate_nids)

from aqt import gui_hooks
gui_hooks.profile_did_open.append(init_addon)

