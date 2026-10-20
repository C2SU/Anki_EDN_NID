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
    orig_fk = None

    try:
        with codecs.open(mapping_file, "r", "utf-8") as f:
            lines = f.readlines()

        local_notes = dict(mw.col.db.all("SELECT guid, id FROM notes"))
        existing_ids = set(local_notes.values())
        now = int(time.time())

        # Pre-validation: detect duplicate admin_nids in mapping and collisions
        planned_updates = []
        target_admin_nids = set()

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
                if admin_nid in existing_ids or admin_nid in target_admin_nids:
                    # Collision detected: skip to avoid duplicate primary keys
                    continue
                target_admin_nids.add(admin_nid)
                planned_updates.append((admin_nid, now, local_nid))

        if planned_updates:
            orig_fk = mw.col.db.scalar("PRAGMA foreign_keys")
            mw.col.db.execute("PRAGMA foreign_keys = OFF")

            mw.col.db.executemany(
                "UPDATE notes SET id = ?, mod = ?, usn = -1 WHERE id = ?",
                planned_updates,
            )
            mw.col.db.executemany(
                "UPDATE cards SET nid = ?, mod = ?, usn = -1 WHERE nid = ?",
                planned_updates,
            )
            updated = len(planned_updates)
            mw.col.setMod()
            mw.col.save()

    except Exception as e:
        if mw.progress:
            mw.progress.finish()
        showCritical(f"Une erreur est survenue lors de la migration :\n{str(e)}")
        return
    finally:
        try:
            if orig_fk is not None:
                mw.col.db.execute(f"PRAGMA foreign_keys = {1 if orig_fk else 0}")
            else:
                mw.col.db.execute("PRAGMA foreign_keys = ON")
        except Exception:
            pass
        if mw.progress:
            mw.progress.finish()
        if hasattr(mw.col, "reset"):
            mw.col.reset()
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


_nid_addon_initialized = False

def init_addon():
    global _nid_addon_initialized
    if _nid_addon_initialized:
        return
    _nid_addon_initialized = True

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

