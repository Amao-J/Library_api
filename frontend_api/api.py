from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from ninja import NinjaAPI, Schema, Field
from ninja.pagination import paginate, PageNumberPagination
from .models import User, Book, BorrowedBook
import redis
import threading

api = NinjaAPI(urls_namespace="frontend")

redis_client = redis.Redis(host='localhost', port=6379, db=0)


class UserSchema(Schema):
    email: str = Field(..., description="User's email address", example="user@example.com")
    first_name: str = Field(..., description="User's first name", example="John")
    last_name: str = Field(..., description="User's last name", example="Doe")

class BookSchema(Schema):
    id: int
    title: str
    author: str
    publisher: str
    category: str
    is_available: bool

class BorrowBookSchema(Schema):
    user_id: int = Field(..., description="ID of the user borrowing the book", example=1)
    days: int = Field(..., description="Number of days to borrow the book", example=7)

@api.post("/users", summary="Enroll a new user", description="Enrolls a new user into the library.")
def enroll_user(request, payload: UserSchema):
    user = User.objects.create(**payload.model_dump()) 
    return {"id": user.id,
            "message": "User enrolled successfully"}

@api.get("/books", response=list[BookSchema], summary="List available books", description="Lists all available books, optionally filtered by publisher or category.")
@paginate(PageNumberPagination, page_size=10)
def list_books(request, publisher: str = None, category: str = None):
    books = Book.objects.filter(is_available=True)
    if publisher:
        books = books.filter(publisher=publisher)
    if category:
        books = books.filter(category=category)
    return books

@api.get("/books/{id}", response=BookSchema, summary="Get a book by ID", description="Retrieves a single book by its ID.")
def get_book(request, id: int):
    return get_object_or_404(Book, id=id)

@api.post("/books/{id}/borrow", summary="Borrow a book", description="Allows a user to borrow a book for a specified number of days.")
def borrow_book(request, id: int, payload: BorrowBookSchema):
    book = get_object_or_404(Book, id=id, is_available=True)
    user = get_object_or_404(User, id=payload.user_id)

    
    if BorrowedBook.objects.filter(book=book, user=user, returned=False).exists():
        return {"error": "User already borrowed this book and has not returned it"}

    book.is_available = False
    book.save()

    return_date = timezone.now() + timedelta(days=payload.days)
    BorrowedBook.objects.create(user=user, book=book, return_date=return_date, returned=False)  

    return {"success": True, "return_date": return_date.strftime("%Y-%m-%d")}

@api.post("/books/{id}/return", summary="Return a book", description="Returns a borrowed book and updates its availability.")
def return_book(request, id: int):
    book = get_object_or_404(Book, id=id)
    borrowed_book = get_object_or_404(BorrowedBook, book=book, returned=False)  
    book.is_available = True
    book.save()

    borrowed_book.returned = True
    borrowed_book.save()

    return {"success": True}


def listen_for_book_updates():
    """Listen for book updates from the Redis channel."""
    pubsub = redis_client.pubsub()
    pubsub.subscribe("book_added")

    for message in pubsub.listen():
        if message["type"] == "message":
            book_id = int(message["data"])  
            
            book = Book.objects.using("backend_db").get(id=book_id)
            
            Book.objects.create(
                id=book.id,
                title=book.title,
                author=book.author,
                publisher=book.publisher,
                category=book.category,
                is_available=book.is_available
            )


thread = threading.Thread(target=listen_for_book_updates)
thread.daemon = True
thread.start()
