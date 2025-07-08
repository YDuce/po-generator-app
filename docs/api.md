# API Documentation

## Overview

The Inventory Manager App provides a RESTful API for managing purchase orders, users, and organizations. This document describes the available endpoints, their request/response formats, and authentication requirements.

## Authentication

All API endpoints except `/api/auth/*` require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Google OAuth Login

```http
GET /api/auth/google

Response: 302 Redirect to Google OAuth consent screen
```

#### OAuth Callback

```http
GET /api/auth/google/callback

Response: 302 Redirect to frontend with token
Location: /dashboard?token=<jwt_token>
```

#### Token Refresh

```http
POST /api/auth/refresh
Authorization: Bearer <token>

Response: 200 OK
{
    "token": "new_jwt_token",
    "expires_at": "2024-03-21T12:00:00Z",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe"
    }
}
```

#### Logout

```http
GET /api/auth/logout
Authorization: Bearer <token>

Response: 200 OK
{
    "message": "Successfully logged out"
}
```

### Email Login

```http
POST /api/v1/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secret"
}

Response: 200 OK
{
    "token": "<jwt_token>"
}
```

### User Management

#### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <token>

Response: 200 OK
{
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "organisation": {
        "id": 1,
        "name": "Example Corp"
    }
}
```

#### Check Authentication

```http
GET /api/auth/check
Authorization: Bearer <token>

Response: 200 OK
{
    "authenticated": true,
    "user": {
        "id": 1,
        "email": "user@example.com"
    }
}
```

### Organisation Management

#### Get Organisation

```http
GET /api/organisations/{id}
Authorization: Bearer <token>

Response: 200 OK
{
    "id": 1,
    "name": "Example Corp",
    "workspace_folder_id": "folder_id",
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe"
        }
    ]
}
```

#### Update Organisation

```http
PUT /api/organisations/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "New Corp Name",
    "workspace_folder_id": "new_folder_id"
}

Response: 200 OK
{
    "id": 1,
    "name": "New Corp Name",
    "workspace_folder_id": "new_folder_id",
    "updated_at": "2024-03-21T12:00:00Z"
}
```

### Purchase Order Management

#### Create Purchase Order

```http
POST /api/purchase-orders
Authorization: Bearer <token>
Content-Type: application/json

{
    "vendor": "Vendor Name",
    "items": [
        {
            "description": "Item 1",
            "quantity": 2,
            "unit_price": 100.00
        }
    ],
    "delivery_date": "2024-04-01"
}

Response: 201 Created
{
    "id": 1,
    "vendor": "Vendor Name",
    "total_amount": 200.00,
    "status": "draft",
    "created_at": "2024-03-21T12:00:00Z"
}
```

#### Get Purchase Order

```http
GET /api/purchase-orders/{id}
Authorization: Bearer <token>

Response: 200 OK
{
    "id": 1,
    "vendor": "Vendor Name",
    "items": [
        {
            "id": 1,
            "description": "Item 1",
            "quantity": 2,
            "unit_price": 100.00,
            "total": 200.00
        }
    ],
    "total_amount": 200.00,
    "status": "draft",
    "delivery_date": "2024-04-01",
    "created_at": "2024-03-21T12:00:00Z",
    "updated_at": "2024-03-21T12:00:00Z"
}
```

#### List Purchase Orders

```http
GET /api/purchase-orders
Authorization: Bearer <token>
Query Parameters:
  - status: draft|approved|sent
  - vendor: string
  - from_date: YYYY-MM-DD
  - to_date: YYYY-MM-DD
  - page: integer
  - per_page: integer

Response: 200 OK
{
    "items": [
        {
            "id": 1,
            "vendor": "Vendor Name",
            "total_amount": 200.00,
            "status": "draft",
            "created_at": "2024-03-21T12:00:00Z"
        }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10,
    "pages": 1
}
```

#### Update Purchase Order

```http
PUT /api/purchase-orders/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "vendor": "Updated Vendor",
    "items": [
        {
            "id": 1,
            "description": "Updated Item",
            "quantity": 3,
            "unit_price": 150.00
        }
    ],
    "delivery_date": "2024-04-15"
}

Response: 200 OK
{
    "id": 1,
    "vendor": "Updated Vendor",
    "total_amount": 450.00,
    "status": "draft",
    "updated_at": "2024-03-21T12:30:00Z"
}
```

#### Delete Purchase Order

```http
DELETE /api/purchase-orders/{id}
Authorization: Bearer <token>

Response: 204 No Content
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
    "error": "Bad Request",
    "message": "Invalid request parameters",
    "details": {
        "field": ["error message"]
    }
}
```

### 401 Unauthorized

```json
{
    "error": "Unauthorized",
    "message": "Invalid or expired token"
}
```

### 403 Forbidden

```json
{
    "error": "Forbidden",
    "message": "Insufficient permissions"
}
```

### 404 Not Found

```json
{
    "error": "Not Found",
    "message": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
    "error": "Internal Server Error",
    "message": "An unexpected error occurred"
}
```

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1616323200
```

## Pagination

List endpoints support pagination with the following query parameters:

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)

Pagination metadata is included in the response:

```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "per_page": 10,
    "pages": 10
}
```

## Versioning

The API version is included in the URL path:

```http
/api/v1/resource
```

Current version: v1

## CORS

The API supports Cross-Origin Resource Sharing (CORS) with the following configuration:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

## Webhooks

The API supports webhooks for real-time notifications:

### Register Webhook

```http
POST /api/webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
    "url": "https://example.com/webhook",
    "events": ["purchase_order.created", "purchase_order.updated"]
}

Response: 201 Created
{
    "id": 1,
    "url": "https://example.com/webhook",
    "events": ["purchase_order.created", "purchase_order.updated"],
    "secret": "webhook_secret"
}
```

### Webhook Events

```json
{
    "event": "purchase_order.created",
    "data": {
        "id": 1,
        "vendor": "Vendor Name",
        "total_amount": 200.00
    },
    "timestamp": "2024-03-21T12:00:00Z"
}
```

### ShipStation Webhook

```http
POST /api/v1/webhook/shipstation
Content-Type: application/json
X-ShipStation-Signature: <HMAC>

Response Codes:
- 204 Accepted
- 400 Invalid payload or unknown channel → {"error": "..."}
- 403 Forbidden → {"error": "Invalid signature"}
 - 413 Payload too large (over 1 024 bytes)
- 429 Too many requests → {"error": "Too many requests"}
- 500 Server error
```

## Testing

The API includes a test suite with the following endpoints:

### Health Check

```http
GET /api/v1/health

Response: 200 OK
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2024-03-21T12:00:00Z"
}
```

### Test Authentication

```http
GET /api/test/auth
Authorization: Bearer <token>

Response: 200 OK
{
    "authenticated": true,
    "user": {
        "id": 1,
        "email": "user@example.com"
    }
}
``` 