from ninja import NinjaAPI, Schema, Field
from django.shortcuts import get_object_or_404
from ninja.pagination import paginate, PageNumberPagination
from datetime import datetime
from .models import Book, User, BorrowedBook
import redis

api = NinjaAPI(urls_namespace="backend")


redis_client = redis.Redis(host='localhost', port=6379, db=0)

class BookSchema(Schema):
    title: str = Field(..., description="Title of the book", example="Python Programming")
    author: str = Field(..., description="Author of the book", example="John Doe")
    publisher: str = Field(..., description="Publisher of the book", example="Wiley")
    category: str = Field(..., description="Category of the book", example="Technology")

class UserSchema(Schema):
    id: int
    email: str
    firstname: str
    lastname: str

class BorrowedBookSchema(Schema):
    book_id: int
    user_id: int
    borrowed_at: datetime
    return_date: datetime

@api.post("/books", summary="Add a new book", description="Adds a new book to the catalogue.")
def add_book(request, payload: BookSchema):
    book = Book.objects.create(**payload.model_dump())
    redis_client.publish("book_added", str(book.id))
    return {"id": book.id,
            "message": "Book added successfully"}


@api.delete("/books/{id}", summary="Remove a book", description="Removes a book from the catalogue by its ID.")
def remove_book(request, id: int):
    book = get_object_or_404(Book, id=id)
    
    
    if BorrowedBook.objects.filter(book=book, returned=False).exists():
        return {"error": "Cannot delete a book that is currently borrowed"}, 400
    
    book.delete()
    return {"success": True, "message": "Book deleted successfully"}

@api.get("/users", response=list[UserSchema], summary="List users", description="Lists all enrolled users.")
@paginate(PageNumberPagination)
def list_users(request, email: str = None, firstname: str = None):
    users = User.objects.all()
    if email:
        users = users.filter(email__icontains=email)
    if firstname:
        users = users.filter(firstname__icontains=firstname)
    return users

@api.get("/borrowed-books", response=list[BorrowedBookSchema], summary="List borrowed books", description="Lists all borrowed books with user and book details.")
@paginate(PageNumberPagination)
def list_borrowed_books(
    request, 
    user_id: int = Field(None, description="Filter by user ID"), 
    book_id: int = Field(None, description="Filter by book ID")
):
    borrowed_books = BorrowedBook.objects.all()
    if user_id:
        borrowed_books = borrowed_books.filter(user_id=user_id)
    if book_id:
        borrowed_books = borrowed_books.filter(book_id=book_id)
    return borrowed_books