"""Integration tests for workspace functionality."""

import pytest
from app.core.models.user import User
from app.core.models.organisation import Organisation

def test_workspace_creation(client, db_session, mock_drive_service) -> None:
    """Test workspace creation flow."""
    # Create test user
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Login user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Request workspace creation
    response = client.post('/api/woot/workspace')
    assert response.status_code == 201
    workspace_id = response.json['workspace_id']
    
    # Verify workspace was created
    assert workspace_id == 'workspace_id'
    
    # Verify organisation was created
    org = Organisation.query.filter_by(name='test').first()
    assert org is not None
    assert org.workspace_folder_id == workspace_id
    
    # Verify Drive service was called correctly
    mock_drive_service.ensure_workspace.assert_called_once_with(str(org.id))
    mock_drive_service.ensure_subfolder.assert_any_call(workspace_id, 'woot')
    mock_drive_service.ensure_subfolder.assert_any_call(workspace_id, 'porfs')
    mock_drive_service.ensure_subfolder.assert_any_call(workspace_id, 'pos')

def test_workspace_retrieval(client, db_session, mock_drive_service) -> None:
    """Test workspace retrieval flow."""
    # Create test user and organisation
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    org = Organisation(
        name='test',
        workspace_folder_id='test_workspace_id'
    )
    db_session.add(user)
    db_session.add(org)
    db_session.commit()
    
    # Login user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Request workspace
    response = client.get('/api/woot/workspace')
    assert response.status_code == 200
    assert response.json['workspace_id'] == 'test_workspace_id'

def test_workspace_not_found(client, db_session) -> None:
    """Test workspace retrieval when not found."""
    # Create test user without organisation
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Login user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Request workspace
    response = client.get('/api/woot/workspace')
    assert response.status_code == 404
    assert response.json['error'] == 'Workspace not found'

def test_workspace_creation_error(client, db_session, mock_drive_service) -> None:
    """Test workspace creation error handling."""
    # Create test user
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Login user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Simulate Drive service error
    mock_drive_service.ensure_workspace.side_effect = Exception('Drive API Error')
    
    # Request workspace creation
    response = client.post('/api/woot/workspace')
    assert response.status_code == 500
    assert response.json['error'] == 'Failed to create workspace' 