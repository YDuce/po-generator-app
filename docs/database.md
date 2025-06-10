# Database Models and Migrations

## Overview

The PO Generator App uses SQLAlchemy ORM with Alembic for database migrations. This document describes the database models, their relationships, and the migration process.

## Models

### User Model

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    google_id = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organisation = db.relationship('Organisation', backref='users', lazy=True)
    sessions = db.relationship('Session', backref='user', lazy=True)
```

### Organisation Model

```python
class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    workspace_folder_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='organisation', lazy=True)
```

### Session Model

```python
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Relationships

1. **User-Organisation**
   - Many-to-One relationship
   - User belongs to one Organisation
   - Organisation has many Users

2. **User-Session**
   - One-to-Many relationship
   - User can have multiple Sessions
   - Session belongs to one User

## Migrations

### Migration Chain

1. `001_initial.py`
   - Creates initial tables
   - Sets up basic schema

2. `004_add_porf_status_and_relationships.py`
   - Adds PORF status fields
   - Updates model relationships

3. `009_update_auth_models.py`
   - Updates authentication models
   - Adds session management

### Creating Migrations

```bash
# Create new migration
flask db migrate -m "description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### Migration Best Practices

1. **Version Control**
   - Keep migrations in version control
   - Never modify existing migrations
   - Create new migrations for changes

2. **Testing**
   - Test migrations in development
   - Verify rollback functionality
   - Check data integrity

3. **Deployment**
   - Run migrations before app start
   - Backup database before migration
   - Monitor migration progress

## Database Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DATABASE_TEST_URL=postgresql://user:password@localhost:5432/test_dbname
```

### SQLAlchemy Configuration

```python
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # Set to True for debugging
```

## Query Examples

### User Queries

```python
# Get user by email
user = User.query.filter_by(email=email).first()

# Get users in organisation
users = User.query.filter_by(organisation_id=org_id).all()

# Get active sessions
sessions = Session.query.filter(
    Session.expires_at > datetime.utcnow()
).all()
```

### Organisation Queries

```python
# Get organisation with users
org = Organisation.query.options(
    joinedload(Organisation.users)
).get(org_id)

# Get organisations with active users
orgs = Organisation.query.join(User).filter(
    User.last_login > datetime.utcnow() - timedelta(days=30)
).all()
```

## Data Integrity

1. **Constraints**
   - Unique email addresses
   - Required fields
   - Foreign key relationships
   - Cascade deletes

2. **Indexes**
   - Primary keys
   - Foreign keys
   - Frequently queried fields
   - Unique constraints

3. **Validation**
   - Model-level validation
   - Data type checking
   - Relationship integrity
   - Business rules

## Backup and Recovery

1. **Backup Strategy**
   - Regular database dumps
   - Point-in-time recovery
   - Transaction logs
   - Backup verification

2. **Recovery Process**
   - Restore from backup
   - Verify data integrity
   - Update application state
   - Monitor system health

## Performance Optimization

1. **Query Optimization**
   - Use appropriate indexes
   - Optimize joins
   - Limit result sets
   - Use eager loading

2. **Connection Management**
   - Connection pooling
   - Timeout settings
   - Error handling
   - Resource cleanup

## Monitoring

1. **Metrics**
   - Query performance
   - Connection usage
   - Disk space
   - Cache hit rates

2. **Alerts**
   - Slow queries
   - Connection errors
   - Space issues
   - Migration failures 