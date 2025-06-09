from app.core.services.drive import DriveService
import types


def test_ensure_workspace(monkeypatch):
    created = []
    flags = {
        "root": False,
        "woot": False,
        "porfs": False,
        "pos": False,
    }

    def fake_list_files(self, query=None):
        if "Your-App-Workspace" in query:
            return [{"id": "root_id"}] if flags["root"] else []
        if "name = 'woot'" in query:
            return [{"id": "woot_id"}] if flags["woot"] else []
        if "name = 'porfs'" in query:
            return [{"id": "porfs_id"}] if flags["porfs"] else []
        if "name = 'pos'" in query:
            return [{"id": "pos_id"}] if flags["pos"] else []
        return []

    def fake_create_folder(self, name, parent_id=None):
        created.append((name, parent_id))
        flags[name.split("-")[-1] if name.startswith("Your-App") else name] = True
        return {"id": f"{name}_id"}

    monkeypatch.setattr(DriveService, "__init__", lambda self, creds: None)
    monkeypatch.setattr(DriveService, "list_files", fake_list_files)
    monkeypatch.setattr(DriveService, "create_folder", fake_create_folder)

    class DummySession:
        def query(self, model):
            class Q:
                def get(self, id):
                    return None

            return Q()

        def add(self, obj):
            pass

        def commit(self):
            pass

    dummy_db = types.SimpleNamespace(session=DummySession())
    monkeypatch.setattr("app.core.services.drive.db", dummy_db)

    svc = DriveService(None)
    root1 = svc.ensure_workspace("1")
    root2 = svc.ensure_workspace("1")

    assert root1 == "Your-App-Workspace-1_id"
    assert root2 == "Your-App-Workspace-1_id"
    assert created == [
        ("Your-App-Workspace-1", None),
        ("woot", "Your-App-Workspace-1_id"),
        ("porfs", "woot_id"),
        ("pos", "woot_id"),
    ]
