from django.test import TestCase
from ninja.testing import TestClient
from .models import User, Book, BorrowedBook
from .api import api
from django.utils import timezone
from datetime import timedelta


class FrontendAPITests(TestCase):
    def setUp(self):
        # Create test data
        self.user = User.objects.create(email="user@example.com", first_name="John", last_name="Doe")
        self.book = Book.objects.create(
            title="Python Programming", 
            author="John Doe", 
            publisher="Wiley", 
            category="Technology"
        )
        self.borrowed_book = BorrowedBook.objects.create(
            book=self.book, 
            user=self.user, 
            return_date=timezone.now() + timedelta(days=7)
        )
        
        # Initialize the Django Ninja TestClient
        self.client = TestClient(api)

    def test_enroll_user(self):
        response = self.client.post("/users", json={"email": "new@example.com", "first_name": "Jane", "last_name": "Doe"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 2)

    def test_borrow_book(self):
        response = self.client.post(f"/books/{self.book.id}/borrow", json={"user_id": self.user.id, "days": 7})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Book.objects.get(id=self.book.id).is_available)
    def test_return_book(self):
        BorrowedBook.objects.create(book=self.book, user=self.user, return_date="2025-03-14", returned=False)
        self.book.is_available = False
        self.book.save()

        response = self.client.post(f"/books/{self.book.id}/return")
        self.assertEqual(response.status_code, 200)
        self.book.refresh_from_db()
        self.assertTrue(self.book.is_available)

        borrowed_book = BorrowedBook.objects.get(book=self.book, user=self.user)
        self.assertTrue(borrowed_book.returned)
