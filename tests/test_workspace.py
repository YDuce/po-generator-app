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
    # Track created folders by (name, parent_id)
    folder_db = {}

    def fake_list_files(self, query=None):
        # Simulate folder lookup by name and parent
        if query is None:
            return []
        if "Your-App-Workspace" in query:
            name = query.split("'")[1]
            for (n, p), fid in folder_db.items():
                if n == name:
                    return [{"id": fid}]
            return []
        if "name = 'woot'" in query:
            for (n, p), fid in folder_db.items():
                if n == "woot" and (p is not None and "Your-App-Workspace" in p):
                    return [{"id": fid}]
            return []
        if "name = 'porfs'" in query:
            for (n, p), fid in folder_db.items():
                if n == "porfs" and p == "woot_id":
                    return [{"id": fid}]
            return []
        if "name = 'pos'" in query:
            for (n, p), fid in folder_db.items():
                if n == "pos" and p == "woot_id":
                    return [{"id": fid}]
            return []
        return []

    def fake_create_folder(self, name, parent_id=None):
        fid = f"{name}_id"
        created.append((name, parent_id))
        folder_db[(name, parent_id)] = fid
        flags[name.split("-")[-1] if name.startswith("Your-App") else name] = True
        return {"id": fid}

    monkeypatch.setattr(DriveService, "__init__", lambda self, creds: None)
    monkeypatch.setattr(DriveService, "list_files", fake_list_files)
    monkeypatch.setattr(DriveService, "create_folder", fake_create_folder)

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