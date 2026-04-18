# Mkulima Digital API Endpoints Documentation

## Base URL
```
http://localhost:8000/api/
```

---

## Authentication Endpoints
**Base:** `/api/auth/`

### 1. User Registration
**POST** `/api/auth/register/`
```json
{
    "email": "farmer@example.com",
    "username": "farmer_name",
    "password": "secure_password",
    "role": "farmer"  // Options: farmer, retailer, customer
}
```
**Response (201):**
```json
{
    "message": "User registered successfully",
    "token": "abc123token",
    "user": {
        "username": "farmer_name",
        "email": "farmer@example.com",
        "role": "farmer"
    }
}
```

### 2. User Login
**POST** `/api/auth/login/`
```json
{
    "email": "farmer@example.com",
    "password": "secure_password"
}
```
**Response (200):**
```json
{
    "message": "Login successful",
    "token": "abc123token",
    "user_details": {
        "email": "farmer@example.com",
        "role": "farmer"
    }
}
```

---

## Products Endpoints
**Base:** `/api/products/`

### 1. List All Products
**GET** `/api/products/`

**Query Parameters:**
- `search` - Search by name, description, location, or farmer email
- `status` - Filter by status (available, out_of_stock, discontinued)
- `category` - Filter by category ID
- `farmer` - Filter by farmer ID or email
- `min_price` - Minimum price filter
- `max_price` - Maximum price filter
- `ordering` - Sort by: price, created_at, quantity

**Example:**
```
GET /api/products/?status=available&category=1&min_price=100&max_price=500
```

**Response (200):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "farmer": 5,
            "farmer_email": "farmer@example.com",
            "category": 1,
            "category_name": "Vegetables",
            "name": "Fresh Tomatoes",
            "description": "Organic tomatoes from my farm",
            "price": "150.00",
            "quantity": 100,
            "unit": "kg",
            "image": "https://res.cloudinary.com/...",
            "location": "Nairobi, Kenya",
            "status": "available",
            "is_in_stock": true,
            "created_at": "2026-04-17T10:30:00Z",
            "updated_at": "2026-04-17T10:30:00Z"
        }
    ]
}
```

### 2. Get Product Details
**GET** `/api/products/{id}/`

**Response (200):** Same as single product from list above

### 3. Create Product (Farmers Only)
**POST** `/api/products/`
**Authentication:** Required (Token)
```json
{
    "category": 1,
    "name": "Fresh Maize",
    "description": "Premium maize from certified farm",
    "price": "250.50",
    "quantity": 500,
    "unit": "kg",
    "image": "<file_upload>",
    "location": "Kisumu, Kenya",
    "status": "available"
}
```
**Response (201):** Product object with all fields

### 4. Update Product (Farmer Owner Only)
**PUT/PATCH** `/api/products/{id}/`
**Authentication:** Required (Token)
```json
{
    "name": "Updated Product Name",
    "price": "300.00",
    "quantity": 450
}
```
**Response (200):** Updated product object

### 5. Delete Product (Farmer Owner Only)
**DELETE** `/api/products/{id}/`
**Authentication:** Required (Token)
**Response (204):** No content

### 6. Get My Products (Farmers Only)
**GET** `/api/products/my_products/`
**Authentication:** Required (Token)
**Response (200):** List of farmer's products

### 7. Update Product Stock
**POST** `/api/products/{id}/update_stock/`
**Authentication:** Required (Token)
```json
{
    "quantity": 250
}
```
**Response (200):** Updated product object

### 8. Update Product Status
**POST** `/api/products/{id}/update_status/`
**Authentication:** Required (Token)
```json
{
    "status": "out_of_stock"
}
```
**Response (200):** Updated product object

---

## Categories Endpoints
**Base:** `/api/products/categories/`

### 1. List All Categories
**GET** `/api/products/categories/`
**Query Parameters:**
- `search` - Search by name
- `ordering` - Sort by name or created_at

**Response (200):**
```json
{
    "count": 10,
    "results": [
        {
            "id": 1,
            "name": "Vegetables",
            "description": "Fresh vegetables from local farms",
            "created_at": "2026-04-17T10:00:00Z",
            "updated_at": "2026-04-17T10:00:00Z"
        }
    ]
}
```

### 2. Get Category Details
**GET** `/api/products/categories/{id}/`
**Response (200):** Single category object

---

## Orders Endpoints
**Base:** `/api/orders/`

### 1. List Orders
**GET** `/api/orders/`
**Authentication:** Required (Token)

**Role-based filtering:**
- **Buyers/Retailers:** See only their own orders
- **Farmers:** See orders containing their products
- **Admin:** See all orders

**Query Parameters:**
- `search` - Search by order_number or buyer email
- `ordering` - Sort by created_at, total_amount, status
- `status` - Filter by status

**Response (200):**
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "order_number": "ORD-12345678",
            "buyer": 2,
            "buyer_email": "buyer@example.com",
            "buyer_username": "buyer_name",
            "status": "pending",
            "total_amount": "450.00",
            "delivery_address": "123 Main St, Nairobi",
            "phone_number": "0712345678",
            "items": [],
            "created_at": "2026-04-17T10:30:00Z",
            "updated_at": "2026-04-17T10:30:00Z",
            "delivered_at": null
        }
    ]
}
```

### 2. Get Order Details
**GET** `/api/orders/{id}/`
**Authentication:** Required (Token)

**Response (200):**
```json
{
    "id": 1,
    "order_number": "ORD-12345678",
    "buyer": 2,
    "buyer_email": "buyer@example.com",
    "buyer_username": "buyer_name",
    "buyer_phone": "John",
    "status": "pending",
    "total_amount": "450.00",
    "delivery_address": "123 Main St, Nairobi",
    "phone_number": "0712345678",
    "items": [
        {
            "id": 1,
            "product": 1,
            "product_details": {
                "id": 1,
                "name": "Fresh Tomatoes",
                "price": "150.00",
                // ... full product object
            },
            "quantity": 3,
            "price_at_purchase": "150.00",
            "subtotal": "450.00",
            "created_at": "2026-04-17T10:30:00Z"
        }
    ],
    "created_at": "2026-04-17T10:30:00Z",
    "updated_at": "2026-04-17T10:30:00Z",
    "delivered_at": null
}
```

### 3. Create Order (Buyers/Retailers Only)
**POST** `/api/orders/`
**Authentication:** Required (Token)
```json
{
    "delivery_address": "456 Second Ave, Nairobi",
    "phone_number": "0712345678",
    "items": [
        {
            "product": 1,
            "quantity": 3
        },
        {
            "product": 2,
            "quantity": 5
        }
    ]
}
```
**Response (201):** Order object with items

### 4. Confirm Order
**POST** `/api/orders/{id}/confirm/`
**Authentication:** Required (Token)
**Allowed:** Order owner or admin
**Changes status:** pending → confirmed

**Response (200):** Updated order object

### 5. Mark Order as Shipped (Admin Only)
**POST** `/api/orders/{id}/ship/`
**Authentication:** Required (Token, Admin)
**Changes status:** confirmed → shipped

**Response (200):** Updated order object

### 6. Mark Order as Delivered (Admin Only)
**POST** `/api/orders/{id}/deliver/`
**Authentication:** Required (Token, Admin)
**Changes status:** shipped → delivered

**Response (200):** Updated order object

### 7. Cancel Order
**POST** `/api/orders/{id}/cancel/`
**Authentication:** Required (Token)
**Allowed:** Order owner or admin
**Note:** Cannot cancel shipped or delivered orders

**Response (200):** Updated order object

### 8. Get My Orders
**GET** `/api/orders/my_orders/`
**Authentication:** Required (Token)
- **Farmers:** See orders for their products
- **Buyers:** See only their orders

**Response (200):** List of orders

### 9. Get Order Statistics (Admin Only)
**GET** `/api/orders/stats/`
**Authentication:** Required (Token, Admin)

**Response (200):**
```json
{
    "total_orders": 150,
    "total_revenue": "45000.00",
    "status_breakdown": {
        "pending": 10,
        "confirmed": 20,
        "shipped": 50,
        "delivered": 65,
        "cancelled": 5
    }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
    "error": "Description of the validation error"
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "error": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

---

## Authentication Header

For all authenticated endpoints, include:
```
Authorization: Token YOUR_TOKEN_HERE
```

Example with curl:
```bash
curl -H "Authorization: Token abc123token" \
  http://localhost:8000/api/products/
```

---

## Order Status Workflow

```
pending → confirmed → shipped → delivered
   ↓
   └──→ cancelled (at any point before shipped)
```

---

## Role-Based Access Control

| Endpoint | Anonymous | Farmer | Buyer | Admin |
|----------|-----------|--------|-------|-------|
| List Products | ✓ | ✓ | ✓ | ✓ |
| Create Product | ✗ | ✓ | ✗ | ✓ |
| Update Own Product | ✗ | ✓ | ✗ | ✓ |
| Delete Own Product | ✗ | ✓ | ✗ | ✓ |
| Create Order | ✗ | ✗ | ✓ | ✓ |
| View Own Orders | ✗ | ✓* | ✓ | ✓ |
| Confirm Order | ✗ | ✗ | ✓** | ✓ |
| Ship Order | ✗ | ✗ | ✗ | ✓ |
| Deliver Order | ✗ | ✗ | ✗ | ✓ |
| Cancel Order | ✗ | ✗ | ✓** | ✓ |
| View Stats | ✗ | ✗ | ✗ | ✓ |

*Farmers see orders for their products
**Only own orders
