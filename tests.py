import unittest
from unittest.mock import patch
from app import app, db, Photo, Category, Contact
from datetime import datetime

class TestPhotographerPortfolio(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Photographer Portfolio', response.data)

    def test_categories_page(self):
        response = self.app.get('/categories')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Categories', response.data)

    def test_category_page(self):
        category = Category(name='Portraits')
        db.session.add(category)
        db.session.commit()

        response = self.app.get('/categories/portraits')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Portraits', response.data)

    def test_photo_page(self):
        category = Category(name='Landscapes')
        db.session.add(category)
        photo = Photo(title='Mountain View', category=category, image_url='mountain.jpg')
        db.session.add(photo)
        db.session.commit()

        response = self.app.get('/photos/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mountain View', response.data)

    def test_about_page(self):
        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    def test_contact_page(self):
        response = self.app.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Contact', response.data)

    def test_contact_form_submission(self):
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Hello, I would like to book a photoshoot.'
        }
        response = self.app.post('/contact', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your message!', response.data)

        contact = Contact.query.filter_by(name='John Doe').first()
        self.assertIsNotNone(contact)
        self.assertEqual(contact.email, 'john@example.com')
        self.assertEqual(contact.message, 'Hello, I would like to book a photoshoot.')

    def test_photo_upload(self):
        with patch('app.Photo.save_image') as mock_save_image:
            mock_save_image.return_value = 'mountain.jpg'
            data = {
                'title': 'Mountain View',
                'category': 1,
                'image': (b'sample_image_data', 'mountain.jpg')
            }
            response = self.app.post('/photos/add', data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Mountain View', response.data)

            photo = Photo.query.filter_by(title='Mountain View').first()
            self.assertIsNotNone(photo)
            self.assertEqual(photo.title, 'Mountain View')
            self.assertEqual(photo.image_url, 'mountain.jpg')

if __name__ == '__main__':
    unittest.main()