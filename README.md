# Library_api
This Library Api is a lightweight, API-driven solution designed to streamline book borrowing It consists of two independent services:  Frontend API: Handles user interactions such as enrolling users and borrowing books. Backend Manages book and user records, ensuring smooth library operations. The system is built with Django-Ninja.


This Library Management System follows a microservices architecture, where the Frontend API (user-facing) and Backend API (admin-facing) communicate to keep book availability updated.

1. Enroll a User
Request:

http
Copy
Edit
POST /frontend-api/users
Body:

json
Copy
Edit
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
Response:

json
Copy
Edit
{ "id": 1 }
2. List Available Books
Request:

http
Copy
Edit
GET /frontend-api/books
Response:

json
Copy
Edit
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
3. Borrow a Book
When a user borrows a book, the Frontend API updates its database and notifies the Backend API.
Frontend API Request:

http
Copy
Edit
POST /frontend-api/books/101/borrow
Body:

json
Copy
Edit
{ "user_id": 1, "days": 7 }
Response:

json
Copy
Edit
{ "success": true, "return_date": "2025-03-14" }
Backend API Updates: It receives a request to mark the book as unavailable.
4. Return a Book
Once returned, the Frontend API updates its records and notifies the Backend API to mark it as available.
Frontend API Request:

http
Copy
Edit
POST /frontend-api/books/101/return
Response:

json
Copy
Edit
{ "success": true }
