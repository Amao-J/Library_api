# Library_api
This Library Api is a lightweight, API-driven solution designed to streamline book borrowing It consists of two independent services:  Frontend API: Handles user interactions such as enrolling users and borrowing books. Backend Manages book and user records, ensuring smooth library operations. The system is built with Django-Ninja.


This Library Management System follows a microservices architecture, where the Frontend API (user-facing) and Backend API (admin-facing) communicate to keep book availability updated.


##  Frontend API (User-Facing)
### **1. Enroll a User**
**Request:**
```http
POST /frontend-api/users
```

```
[
  {
    "id": 101,
    "title": "Python Programming",
    "author": "John Doe",
    "publisher": "Wiley",
    "category": "Technology",
    "is_available": true
  }
]

```

## 2. List Available Books
Request:


```http
GET /frontend-api/books
```


3. Borrow a Book
The Frontend API updates the database and notifies the Backend API.
Request:

```http

POST /frontend-api/books/101/borrow
Body:

json

{ "user_id": 1, "days": 7 }
```
Response:

```json

{ "success": true, "return_date": "2025-03-14" }
```
Backend API Sync: A request is sent to mark the book as unavailable.
4. Return a Book
The Frontend API updates the record and notifies the Backend API.
Request:

```http
POST /frontend-api/books/101/return
````
Response:
```json
{ "success": true }
```
##  Backend API (Admin-Facing)
1. Add a New Book
Request:

```http
POST /backend-api/books
```

Body:

```json

{
  "title": "Python Programming",
  "author": "John Doe",
  "publisher": "Wiley",
  "category": "Technology",
  "is_available": true
}
```
Response:

```json

{ "id": 101 }
```

2. Update Book Details
Request:
```http
PUT /backend-api/books/101

```
Body:

```json

{
  "title": "Advanced Python",
  "author": "John Doe",
  "publisher": "O'Reilly",
  "category": "Technology",
  "is_available": true
}
```

Response:

```json
{ "success": true }
```

