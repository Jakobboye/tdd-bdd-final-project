# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  prod R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_product(self):
        """It should Read a product from the database"""
        product = ProductFactory()
        product.id = None
        product.create()
        assert product is not None
        found_product = product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)

    def test_update_product(self):
        """It should Update a product in the database"""
        product = ProductFactory()
        product.id = None
        product.create()
        product.description = "Test description"
        original_id = product.id
        product.update()
        assert product is not None
        assert product.description == "Test description"

        all_products = product.all()
        self.assertEqual(len(all_products), 1)
        self.assertEqual(all_products[0].id, original_id)
        self.assertEqual(all_products[0].description, "Test description")

    def test_delete_product(self):
        """It should Delete a product from the database"""
        product = ProductFactory()
        product.create()
        all_products = product.all()
        self.assertEqual(len(all_products), 1)

        product.delete()
        all_products = product.all()
        self.assertEqual(len(all_products), 0)

    def test_list_all_products(self):
        """It should List all products in the database"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        for _ in range(5):
            prod = ProductFactory()
            prod.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find products in the database by name"""
        for _ in range(5):
            prod = ProductFactory()
            prod.create()
        products = Product.all()
        name = products[0].name
        name_count = len([prod for prod in products if prod.name == name])
        named_products = Product.find_by_name(name)
        self.assertEqual(named_products.count(), name_count)
        for prod in named_products:
            self.assertEqual(prod.name, name)

    def test_find_by_availability(self):
        """It should Find products in the database by Availability"""
        products = ProductFactory.create_batch(10)
        for prod in products:
            prod.create()
        products = Product.all()
        available = products[0].available
        available_count = len([prod for prod in products if prod.available == available])

        found_products = Product.find_by_availability(available)
        self.assertEqual(found_products.count(), available_count)
        for prod in found_products:
            self.assertEqual(prod.available, available)

    def test_find_by_category(self):
        """It should Find products in the database by Category"""
        products = ProductFactory.create_batch(10)
        for prod in products:
            prod.create()
        products = Product.all()
        cat = products[0].category
        cat_count = len([prod for prod in products if prod.category == cat])

        found_products = Product.find_by_category(cat)
        self.assertEqual(found_products.count(), cat_count)
        for prod in found_products:
            self.assertEqual(prod.category, cat)

    def test_find_by_price(self):
        """It should Find products in the database by Price"""
        products = ProductFactory.create_batch(10)
        for prod in products:
            prod.create()
        products = Product.all()
        price = products[0].price
        price_count = len([prod for prod in products if prod.price == price])

        found_products = Product.find_by_price(price)
        self.assertEqual(found_products.count(), price_count)
        for prod in found_products:
            self.assertEqual(prod.price, price)
