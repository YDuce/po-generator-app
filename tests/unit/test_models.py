# """Unit tests for database models."""
#
# import pytest
# from datetime import datetime
# from app.core.auth.models import User
# from app.core.models.organisation import Organisation
# from app.channels.woot.models import WootPorf, WootPorfLine, WootPorfStatus
#
# def test_user_model(db_session):
#     """Test User model."""
#     # Create user
#     user = User(
#         email='test@example.com',
#         name='Test User',
#         google_id='123456789'
#     )
#     db_session.add(user)
#     db_session.commit()
#
#     # Verify user was created
#     assert user.id is not None
#     assert user.email == 'test@example.com'
#     assert user.name == 'Test User'
#     assert user.google_id == '123456789'
#     assert isinstance(user.created_at, datetime)
#     assert isinstance(user.updated_at, datetime)
#
#     # Test unique constraints
#     duplicate_user = User(
#         email='test@example.com',
#         name='Another User',
#         google_id='987654321'
#     )
#     db_session.add(duplicate_user)
#     with pytest.raises(Exception):
#         db_session.commit()
#     db_session.rollback()
#
# def test_organisation_model(db_session):
#     """Test Organisation model."""
#     # Create organisation
#     org = Organisation(
#         name='Test Org',
#         workspace_folder_id='workspace_123'
#     )
#     db_session.add(org)
#     db_session.commit()
#
#     # Verify organisation was created
#     assert org.id is not None
#     assert org.name == 'Test Org'
#     assert org.workspace_folder_id == 'workspace_123'
#     assert isinstance(org.created_at, datetime)
#     assert isinstance(org.updated_at, datetime)
#
#     # Test unique constraints
#     duplicate_org = Organisation(
#         name='Test Org',
#         workspace_folder_id='workspace_456'
#     )
#     db_session.add(duplicate_org)
#     with pytest.raises(Exception):
#         db_session.commit()
#     db_session.rollback()
#
# def test_woot_porf_model(db_session):
#     """Test WootPorf model."""
#     # Create PORF
#     porf = WootPorf(
#         porf_no='PORF-001',
#         status=WootPorfStatus.DRAFT,
#         total_value=1000.00
#     )
#     db_session.add(porf)
#     db_session.commit()
#
#     # Verify PORF was created
#     assert porf.id is not None
#     assert porf.porf_no == 'PORF-001'
#     assert porf.status == WootPorfStatus.DRAFT
#     assert float(porf.total_value) == 1000.00
#     assert isinstance(porf.created_at, datetime)
#     assert isinstance(porf.updated_at, datetime)
#
#     # Test unique constraints
#     duplicate_porf = WootPorf(
#         porf_no='PORF-001',
#         status=WootPorfStatus.DRAFT,
#         total_value=2000.00
#     )
#     db_session.add(duplicate_porf)
#     with pytest.raises(Exception):
#         db_session.commit()
#     db_session.rollback()
#
# def test_woot_porf_line_model(db_session):
#     """Test WootPorfLine model."""
#     # Create PORF
#     porf = WootPorf(
#         porf_no='PORF-001',
#         status=WootPorfStatus.DRAFT,
#         total_value=1000.00
#     )
#     db_session.add(porf)
#     db_session.commit()
#
#     # Create PORF line
#     line = WootPorfLine(
#         porf=porf,
#         product_id='PROD-001',
#         product_name='Test Product',
#         quantity=10,
#         unit_price=100.00,
#         total_price=1000.00
#     )
#     db_session.add(line)
#     db_session.commit()
#
#     # Verify PORF line was created
#     assert line.id is not None
#     assert line.porf_id == porf.id
#     assert line.product_id == 'PROD-001'
#     assert line.product_name == 'Test Product'
#     assert line.quantity == 10
#     assert float(line.unit_price) == 100.00
#     assert float(line.total_price) == 1000.00
#     assert isinstance(line.created_at, datetime)
#     assert isinstance(line.updated_at, datetime)
#
#     # Test relationship
#     assert line.porf == porf
#     assert line in porf.lines
#
# def test_models_init() -> None:
#     pass
#
# def test_models_create() -> None:
#     pass
#
# def test_models_update() -> None:
#     pass