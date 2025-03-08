from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from ninja.testing import TestClient
from .models import User, Book, BorrowedBook
from .api import api

class BackendAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@example.com", first_name="John", last_name="Doe")
        self.book = Book.objects.create(
            title="Python Programming", 
            author="John Doe", 
            publisher="Wiley", 
            category="Technology"
        )
        self.client = TestClient(api)

    def test_add_book(self):
        response = self.client.post(
            "/books", 
            json={"title": "New Book", "author": "Jane Doe", "publisher": "Apress", "category": "Fiction"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), 2)

    def test_remove_book(self):
        response = self.client.delete(f"/books/{self.book.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), 0)

    def test_list_users(self):
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_list_borrowed_books(self):
        BorrowedBook.objects.create(
            book=self.book, 
            user=self.user, 
            borrowed_date=timezone.now(), 
            return_date=timezone.now() + timedelta(days=7),
            returned=False
        )
        response = self.client.get("/borrowed-books")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)