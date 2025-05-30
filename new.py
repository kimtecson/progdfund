import sys
from datetime import datetime
import os
from collections import defaultdict
import traceback


class InvalidNameError(Exception):
    #Raised when a name contains non-alphabet characters
    pass

class BookNotFoundError(Exception):
    #Raised when a book is not found
    pass

class InvalidDaysError(Exception):
    #Raised when number of borrowing days is invalid
    pass

class ReferenceBookLimitError(Exception):
    #Raised when trying to borrow reference book for more than 14 days
    pass


class Customer:

    def __init__(self, customer_id, name):
        if not name.replace(' ', '').isalpha():
            raise InvalidNameError("Name must contain only alphabet characters and spaces")
        self.id = customer_id
        self.name = name
        self.customer_type = 'C'

    def display_info(self):
        print(f"ID: {self.id}, Name: {self.name}")

class Member(Customer):
    #Customer with discount benefits
    __discount_rate = 0.10  # default 10%

    def __init__(self, customer_id, name, discount_rate=None):
        super().__init__(customer_id, name)
        self.customer_type = 'M'
        if discount_rate is not None:
            self.__discount_rate = discount_rate

    @property
    def discount_rate(self):
        return self.__discount_rate

    @staticmethod
    def set_discount_rate(new_rate):
        if not 0 < new_rate < 1:
            raise ValueError("Discount rate must be between 0 and 1")
        Member.discount_rate = new_rate

    def get_discount(self, rental_cost):
        return rental_cost * self.discount_rate

    def display_info(self):
        print(f"ID: {self.id}, Name: {self.name}, Discount Rate: {self.discount_rate*100}%")

class GoldMember(Customer):
    #Member with discount and reward benefits
    __gold_discount_rate = 0.12  #default 12%

    def __init__(self, customer_id, name, discount_rate=None, reward_rate=1.0, reward_points=0):
        super().__init__(customer_id, name)
        self.customer_type = 'G'
        if discount_rate is not None:
            self.__gold_discount_rate = discount_rate
        self.__reward_rate = reward_rate
        self.reward_points = reward_points

    @property
    def discount_rate(self):
        return self.__gold_discount_rate

    @property
    def reward_rate(self):
        return self.__reward_rate

    @staticmethod
    def set_discount_rate(new_rate):
        if not 0 < new_rate < 1:
            raise ValueError("Discount rate must be between 0 and 1")
        GoldMember.gold_discount_rate = new_rate

    def get_discount(self, rental_cost):
        return rental_cost * self.discount_rate

    @reward_rate.setter
    def reward_rate(self, value):
        if value <= 0:
            raise ValueError("Reward rate must be positive")
        self.__reward_rate = value

    def get_reward(self, amount):
        return round(amount * self.reward_rate)

    def update_reward(self, value):
        new_balance = self.reward_points + value
        if new_balance < 0:
            raise ValueError("Reward points balance cannot go negative")
        self.reward_points = new_balance

    def set_reward_rate(self, new_rate):
        self.reward_rate = new_rate

    def display_info(self):
        """Display complete member information"""
        print(f"ID: {self.id}, Name: {self.name}, "
              f"Discount Rate: {self.discount_rate*100:.1f}%, "
              f"Reward Rate: {self.reward_rate*100:.1f}%, "
              f"Reward Points: {self.reward_points}")

class Book:
    """Class representing a book"""
    def __init__(self, book_id, name, category=None):
        self.id = book_id
        self.name = name
        self.category = category

    def get_price(self, days):
        if self.category:
            return self.category.get_price(days)
        return 0

    def display_info(self):
        category_name = self.category.name if self.category else "None"
        print(f"ID: {self.id}, Name: {self.name}, Category: {category_name}")

class BookCategory:
    """Class representing a book category"""
    def __init__(self, category_id, name, price_1, price_2, category_type="Rental"):
        self.id = category_id
        self.name = name
        self.price_1 = price_1  # Price per day for first tier
        self.price_2 = price_2  # Price per day for second tier
        self.__type = category_type
        self.books = []

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, new_type):
        self.__type = new_type

    def set_prices(self, price_1, price_2):
        self.price_1 = price_1
        self.price_2 = price_2

    def add_book(self, book):
        if book not in self.books:
            self.books.append(book)
            book.category = self

    def remove_book(self, book):
        if book in self.books:
            self.books.remove(book)
            book.category = None

    def get_price(self, days):
        if days <= 7:
            return days * self.price_1
        else:
            return 7 * self.price_1 + (days - 7) * self.price_2

    def display_info(self):
        book_names = [book.name for book in self.books]
        print(f"ID: {self.id}, Name: {self.__name}, Type: {self.type}, "
              f"Price 1: {self.price_1}, Price 2: {self.price_2}, Books: {', '.join(book_names)}")

class BookSeries(Book):
    def __init__(self, series_id, name, books):
        super().__init__(series_id, name)
        self.books = books
        # All books in series should belong to same category
        if books:
            self.category = books[0].category
            for book in books:
                if book.category != self.category:
                    raise ValueError("All books in series must belong to same category")

    def get_price(self, days):
        # Price is 50% of total individual book prices
        total = sum(book.get_price(days) for book in self.books)
        return total * 0.5

    def display_info(self):
        book_names = [book.name for book in self.books]
        category_name = self.category.name if self.category else "None"
        print(f"ID: {self.id}, Name: {self.name}, Category: {category_name}, "
              f"Books in Series: {', '.join(book_names)}")

# Order Class
class Rental:
    """Class representing a rental transaction with HD features"""
    def __init__(self, customer, books_and_days, timestamp=None):
        self.customer = customer
        self.books_and_days = books_and_days  # List of tuples (book, days)
        self.timestamp = timestamp if timestamp else datetime.now()
        self.calculate_costs()

    def calculate_costs(self):
        """Calculate all cost components"""
        # Calculate original cost
        self.original_cost = sum(book.get_price(days) for book, days in self.books_and_days)

        # Apply discount
        if isinstance(self.customer, GoldMember):
            self.discount = self.customer.get_discount(self.original_cost)
            temp_total = self.original_cost - self.discount
            self.reward = self.customer.get_reward(temp_total)

            # Apply reward points deduction if applicable
            points_to_use = (self.customer.reward_points // 20) * 20
            if points_to_use > 0:
                deduction = points_to_use / 20  # Every 20 points = 1 AUD
                temp_total -= deduction
                self.customer.reward_points -= points_to_use

            self.total_cost = temp_total
            # Still add new rewards even if we used some points
            self.customer.update_reward(self.reward)

        elif isinstance(self.customer, Member):
            self.discount = self.customer.get_discount(self.original_cost)
            self.total_cost = self.original_cost - self.discount
        else:  # Regular customer
            self.discount = 0
            self.total_cost = self.original_cost

    def display_receipt(self):
        """Display detailed receipt for the rental"""
        print("\n---")
        print(f"Receipt for {self.customer.name}")
        print(f"Date: {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        print("---")
        print("Books rented:")
        for book, days in self.books_and_days:
            print(f"- {book.name} for {days} days")
        print("---")
        print(f"Original cost: {self.original_cost:.2f} (AUD)")
        print(f"Discount: {self.discount:.2f} (AUD)")
        print(f"Total cost: {self.total_cost:.2f} (AUD)")
        if isinstance(self.customer, GoldMember):
            print(f"Reward earned: {self.reward}")
        print()

# Records Class
class Records:
    """Central data repository with HD level features"""
    def __init__(self):
        self.customers = []
        self.book_categories = []
        self.books = []
        self.rentals = []
        self._customer_rentals = defaultdict(list)  # Track rentals by customer


    def read_customers(self, filename):
        """Read customer data from file"""
        try:
            with open(filename, 'r') as file:
                for line in file:
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) < 3:
                        continue

                    customer_type = parts[0]
                    customer_id = parts[1]
                    name = parts[2]

                    try:
                        if customer_type == 'C':
                            self.customers.append(Customer(customer_id, name))
                        elif customer_type == 'M':
                            discount_rate = float(parts[3]) if parts[3] != 'na' else None
                            self.customers.append(Member(customer_id, name, discount_rate))
                        elif customer_type == 'G':
                            discount_rate = float(parts[3]) if parts[3] != 'na' else None
                            reward_rate = float(parts[4]) if parts[4] != 'na' else 1.0
                            reward_points = int(parts[5]) if parts[5] != 'na' else 0
                            self.customers.append(GoldMember(customer_id, name, discount_rate, reward_rate, reward_points))
                    except (ValueError, InvalidNameError) as e:
                        print(f"Error processing customer line: {line.strip()}. Error: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Customer file {filename} not found")

    def read_books_and_book_categories(self, books_file, categories_file):
        """Read book and category data from files"""
        # First read all books
        try:
            with open(books_file, 'r') as file:
                for line in file:
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 2:
                        book_id = parts[0]
                        book_name = parts[1]
                        # Check if it's a book series (CREDIT level)
                        if book_id.startswith('S') and len(parts) > 2:
                            # Find component books
                            component_books = []
                            for book_name in parts[2:]:
                                book = self.find_book(book_name)
                                if book:
                                    component_books.append(book)
                            if component_books:
                                try:
                                    self.books.append(BookSeries(book_id, parts[1], component_books))
                                except ValueError as e:
                                    print(f"Error creating book series: {e}")
                        else:
                            self.books.append(Book(book_id, book_name))
        except FileNotFoundError:
            raise FileNotFoundError(f"Book file {books_file} not found")

        # Then read categories and assign books to them
        try:
            with open(categories_file, 'r') as file:
                for line in file:
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 5:
                        category_id = parts[0]
                        category_name = parts[1]
                        # Check if type is specified (CREDIT level)
                        if parts[2] in ['Rental', 'Reference']:
                            category_type = parts[2]
                            price_1 = float(parts[3])
                            price_2 = float(parts[4])
                            book_names = parts[5:]
                        else:  # PASS level format
                            category_type = "Rental"
                            price_1 = float(parts[2])
                            price_2 = float(parts[3])
                            book_names = parts[4:]

                        try:
                            category = BookCategory(category_id, category_name, price_1, price_2, category_type)
                            self.book_categories.append(category)

                            for book_name in book_names:
                                book = self.find_book(book_name)
                                if book:
                                    category.add_book(book)
                        except ValueError as e:
                            print(f"Error processing category line: {line.strip()}. Error: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Category file {categories_file} not found")

    def read_rentals(self, rental_file):
        try:
            with open(rental_file, 'r') as file:
                for line in file:
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) < 7:
                        continue

                    customer_id = parts[0]
                    customer = self.find_customer(customer_id)
                    if not customer:
                        continue

                    books_and_days = []
                    i = 1
                    while i < len(parts) - 6:
                        book_id = parts[i]
                        days_str = parts[i+1]

                        book = self.find_book(book_id)
                        if book:
                            try:
                                days = int(days_str)
                                books_and_days.append((book, days))
                            except ValueError:
                                pass
                        i += 2

                    try:
                        timestamp = datetime.strptime(parts[-1], '%d/%m/%Y %H:%M:%S')
                    except ValueError:
                        timestamp = datetime.now()

                    rental = Rental(customer, books_and_days, timestamp)
                    self.add_rental(rental)

        except FileNotFoundError:
            print(f"Rental file '{rental_file}' not found.")

    def find_customer(self, search_value):
        #Find customer by ID or name
        for customer in self.customers:
            if customer.id == search_value or customer.name.lower() == search_value.lower():
                return customer
        return None

    def find_book_category(self, search_value):
        #Find book category by ID or name
        for category in self.book_categories:
            if category.id.lower() == search_value.lower() or category.name.lower() == search_value.lower():
                return category
        return None

    def find_book(self, search_value):
        """Find book by ID or name"""
        for book in self.books:
            if book.id.lower() == search_value.lower() or book.name.lower() == search_value.lower():
                return book
        return None

    def list_customers(self):
        """Display all customers"""
        print("\nList of Customers:")
        for customer in self.customers:
            customer.display_info()
        print()

    def list_books(self):
        """Display all books"""
        print("\nList of Books:")
        for book in self.books:
            book.display_info()
        print()

    def list_book_categories(self):
        """Display all book categories"""
        print("\nList of Book Categories:")
        for category in self.book_categories:
            category.display_info()
        print()

    def add_rental(self, rental):
        """Add a new rental to records"""
        self.rentals.append(rental)
        self._customer_rentals[rental.customer.id].append(rental)
        self.rentals_modified = True

    def process_rental_file(self, filename):

        try:
            with open(filename, 'r') as file:
                for line in file:
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) < 7:  # Minimum valid line
                        continue

                    # Parse customer
                    customer_input = parts[0]
                    customer = self.find_customer(customer_input)
                    if not customer:
                        print(f"Customer {customer_input} not found in line: {line}")
                        continue

                    # Parse books and days (alternating pattern)
                    books_and_days = []
                    i = 1
                    while i < len(parts) - 6:  # Last 6 parts are cost info and timestamp
                        book_input = parts[i]
                        days_str = parts[i+1] if i+1 < len(parts) else '0'

                        book = self.find_book(book_input)
                        if not book:
                            print(f"Book {book_input} not found in line: {line}")
                            break

                        try:
                            days = int(days_str)
                            if days <= 0:
                                raise ValueError
                            # Check reference book limit
                            if book.category and book.category.type == "Reference" and days > 14:
                                raise ReferenceBookLimitError("Reference books cannot be borrowed for more than 14 days")
                        except ValueError:
                            print(f"Invalid days {days_str} in line: {line}")
                            break
                        except ReferenceBookLimitError as e:
                            print(f"{e} in line: {line}")
                            break

                        books_and_days.append((book, days))
                        i += 2

                    if not books_and_days:
                        continue

                    # Parse timestamp
                    try:
                        timestamp = datetime.strptime(parts[-1], '%d/%m/%Y %H:%M:%S')
                    except ValueError:
                        timestamp = datetime.now()

                    # Create rental (skip cost info as we'll recalculate)
                    rental = Rental(customer, books_and_days, timestamp)
                    self.add_rental(rental)

                    # For Gold members, update reward points from file if provided
                    if isinstance(customer, GoldMember) and parts[-2] != 'na':
                        try:
                            reward = int(parts[-2])
                            customer.update_reward(reward)
                        except ValueError:
                            pass

            print(f"Successfully processed rentals from {filename}")
        except FileNotFoundError:
            print(f"Cannot find the rental file {filename}")

    def get_most_valuable_customer(self):
        """Find customer who spent the most (HD level)"""
        customer_spending = defaultdict(float)

        for rental in self.rentals:
            customer_id = rental.customer.id
            customer_spending[customer_id] += rental.total_cost

        if not customer_spending:
            return None

        max_id = max(customer_spending.items(), key=lambda x: x[1])[0]
        return self.find_customer(max_id)

    def get_customer_rental_history(self, customer_id):
        """Get rental history for a customer (HD level)"""
        rentals = self._customer_rentals.get(customer_id, [])
        if not rentals:
            return None

        history = []
        for i, rental in enumerate(rentals, 1):
            books_info = ", ".join(
                f"{book.name}: {days} days"
                for book, days in rental.books_and_days
            )

            history.append({
                'rental_num': i,
                'books_info': books_info,
                'original_cost': rental.original_cost,
                'discount': rental.discount,
                'total_cost': rental.total_cost,
                'reward': rental.reward if isinstance(rental.customer, GoldMember) else 'na',
                'timestamp': rental.timestamp
            })

        return history

    def save_customers(self, customer_file):
        with open(customer_file, 'w') as file:
            for customer in self.customers:
                if isinstance(customer, GoldMember):
                    file.write(f"G, {customer.id}, {customer.name}, {customer.discount_rate}, {customer.reward_rate}, {customer.reward_points}\n")
                elif isinstance(customer, Member):
                    file.write(f"M, {customer.id}, {customer.name}, {customer.discount_rate}, na, na\n")
                else:
                    file.write(f"C, {customer.id}, {customer.name}, na, na, na\n")

    def save_rentals(self, rental_file):
        with open(rental_file, 'w') as file:
            for rental in self.rentals:
                customer = rental.customer
                books_info = []
                for book, days in rental.books_and_days:
                    books_info.append(book.id)
                    books_info.append(str(days))

                if isinstance(customer, GoldMember):
                    file.write(f"{customer.id}, {', '.join(books_info)}, {rental.original_cost:.2f}, {rental.discount:.2f}, {rental.total_cost:.2f}, {rental.reward}, {rental.timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n")
                elif isinstance(customer, Member):
                    file.write(f"{customer.id}, {', '.join(books_info)}, {rental.original_cost:.2f}, {rental.discount:.2f}, {rental.total_cost:.2f}, na, {rental.timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n")
                else:
                    file.write(f"{customer.id}, {', '.join(books_info)}, {rental.original_cost:.2f}, 0.00, {rental.total_cost:.2f}, na, {rental.timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n")

    def save_books_and_categories(self, book_file, category_file):
        with open(book_file, 'w') as file:
            for book in self.books:
                if isinstance(book, BookSeries):
                    book_names = [b.name for b in book.books]
                    file.write(f"{book.id}, {book.name}, {', '.join(book_names)}\n")
                else:
                    file.write(f"{book.id}, {book.name}\n")

        with open(category_file, 'w') as file:
            for category in self.book_categories:
                book_names = [book.name for book in category.books]
                file.write(f"{category.id}, {category.name}, {category.type}, {category.price_1}, {category.price_2}, {', '.join(book_names)}\n")

    # Keep existing save_data as backup if full save is needed
    def save_data(self, customer_file, book_file, category_file, rental_file):
        self.save_customers(customer_file)
        self.save_books_and_categories(book_file, category_file)
        self.save_rentals(rental_file)
    # def save_data(self, customer_file, book_file, category_file, rental_file):
    #     # Save customers
    #     if self.customers_modified:
    #         with open(customer_file, 'w') as file:
    #             for customer in self.customers:
    #                 if isinstance(customer, GoldMember):
    #                     file.write(f"G, {customer.id}, {customer.name}, "
    #                             f"{customer.discount_rate}, {customer.reward_rate}, {customer.reward_points}\n")
    #                 elif isinstance(customer, Member):
    #                     file.write(f"M, {customer.id}, {customer.name}, {customer.discount_rate}, na, na\n")
    #                 else:
    #                     file.write(f"C, {customer.id}, {customer.name}, na, na, na\n")

    #     # Save books (simplified - doesn't preserve series relationships)
    #     with open(book_file, 'w') as file:
    #         for book in self.books:
    #             if isinstance(book, BookSeries):
    #                 book_names = [b.name for b in book.books]
    #                 file.write(f"{book.id}, {book.name}, {', '.join(book_names)}\n")
    #             else:
    #                 file.write(f"{book.id}, {book.name}\n")

    #     # Save categories
    #     with open(category_file, 'w') as file:
    #         for category in self.book_categories:
    #             book_names = [book.name for book in category.books]
    #             file.write(f"{category.id}, {category.name}, {category.type}, "
    #                       f"{category.price_1}, {category.price_2}, {', '.join(book_names)}\n")

    #     # Save rentals (HD level)
    #     with open(rental_file, 'w') as file:
    #         for rental in self.rentals:
    #             customer = rental.customer
    #             books_info = []
    #             for book, days in rental.books_and_days:
    #                 books_info.append(book.id)
    #                 books_info.append(str(days))

    #             if isinstance(customer, GoldMember):
    #                 file.write(f"{customer.id}, {', '.join(books_info)}, "
    #                           f"{rental.original_cost:.2f}, {rental.discount:.2f}, {rental.total_cost:.2f}, {rental.reward}, "
    #                           f"{rental.timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n")
    #             elif isinstance(customer, Member):
    #                 file.write(f"{customer.id}, {', '.join(books_info)}, "
    #                           f"{rental.original_cost:.2f}, {rental.discount:.2f}, {rental.total_cost:.2f}, na, "
    #                           f"{rental.timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n")
    #             else:
    #                 file.write(f"{customer.id}, {', '.join(books_info)}, "
    #                           f"{rental.original_cost:.2f}, 0.00, {rental.total_cost:.2f}, na, "
    #                           f"{rental.timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n")

# Operations Class
class Operations:
    def __init__(self):
        self.records = Records()
        self.load_data()

    def load_data(self):
        """Load data from files with command line arguments or defaults"""
        # Default file names
        customer_file = "customers.txt"
        book_file = "books.txt"
        category_file = "book_categories.txt"
        rental_file = "rentals.txt"

        # Check command line arguments
        if len(sys.argv) == 4:
            customer_file = sys.argv[1]
            book_file = sys.argv[2]
            category_file = sys.argv[3]
        elif len(sys.argv) > 1:
            print("Usage: python program.py [customer_file book_file category_file]")
            sys.exit(1)

        try:
            self.records.read_customers(customer_file)
            self.records.read_books_and_book_categories(book_file, category_file)
            self.records.read_rentals(rental_file)
            print("Data loaded successfully!")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)

    def rent_book(self):
        """Handle book rental process"""
        print("\nRent a Book")

        customer = None
        is_new_customer = False

        while customer is None:
            customer_input = input("Enter customer ID or name: ").strip()
            if not customer_input:
                print("Operation cancelled.")
                return

            existing_customer = self.records.find_customer(customer_input)
            if existing_customer:
                customer = existing_customer
            else:
                print("This customer is not in our system.")
                name = customer_input
                if name.replace(" ", "").isalpha():
                    customer = Customer("TEMP", name)  # temporary ID
                    customer = self.register_customer(customer)
                    is_new_customer = True
                else:
                    print("Invalid name. Try again.")
                    customer = None
        # Get multiple books and days
        books_and_days = []
        while True:
            # Get book
            while True:
                book_input = input("Enter book ID or name (or 'done' to finish): ").strip()
                if book_input.lower() == 'done':
                    break

                book = self.records.find_book(book_input)
                if book:
                    # Check if book is reference type
                    if book.category and book.category.type == "Reference":
                        print("Note: This is a reference book with 14-day limit.")
                    break
                print("Book not found. Please try again.")

            if book_input.lower() == 'done':
                if not books_and_days:
                    print("You must add at least one book")
                    continue
                break

            # Get borrowing days
            while True:
                try:
                    days = int(input(f"Enter number of borrowing days for {book.name}: "))
                    if days <= 0:
                        raise InvalidDaysError("Days must be positive")

                    # Check reference book limit
                    if book.category and book.category.type == "Reference" and days > 14:
                        raise ReferenceBookLimitError("Reference books cannot be borrowed for more than 14 days")

                    books_and_days.append((book, days))
                    break
                except ValueError:
                    print("Please enter a valid number")
                except (InvalidDaysError, ReferenceBookLimitError) as e:
                    print(e)

        # Ask to register if this was a new customer
        if is_new_customer:
            ans = input('Do you want to register as a member and get discounts? (y/n)').strip()
            if ans.lower() == 'y':
                # Remove the old temporary customer
                if customer in self.records.customers:
                    self.records.customers.remove(customer)
                # Create a new Member instance with same ID and name
                member = Member(customer.id, customer.name)
                # Add the new Member to the records
                self.records.customers.append(member)
                # Update the customer reference
                customer = member
                print(customer.discount_rate)
                print(f"{customer.name} has been registered as a Member.")

        # Create and process rental
        rental = Rental(customer, books_and_days)
        rental.display_receipt()
        self.records.add_rental(rental)


    def register_customer(self, customer):
        customer_id = f"M{len(self.records.customers) + 1:03d}"
        new_customer = Member(customer_id, customer.name)
        self.records.customers.append(new_customer)
        print(f"{customer.name} has been registered as a Member with ID {customer_id}.")
        return new_customer




    def update_book_category(self):
        """Update book category information (DI level)"""
        print("\nUpdate Book Category")

        # Find category
        category = None
        while not category:
            search = input("Enter category ID or name: ").strip()
            category = self.records.find_book_category(search)
            if not category:
                print("Category not found. Try again or press Enter to cancel.")
                if not search:
                    return

        # Display current info
        print("\nCurrent category information:")
        category.display_info()

        # Get updates
        print("\nEnter new values (press Enter to keep current):")

        # Update type
        while True:
            new_type = input(f"Type [Rental/Reference] (current: {category.type}): ").strip().title()
            if not new_type:
                break
            if new_type in ['Rental', 'Reference']:
                category.type = new_type
                break
            print("Invalid type. Must be 'Rental' or 'Reference'")

        # Update prices
        while True:
            try:
                price_1 = input(f"Price 1 (current: {category.price_1}): ").strip()
                if price_1:
                    category.price_1 = float(price_1)

                price_2 = input(f"Price 2 (current: {category.price_2}): ").strip()
                if price_2:
                    category.price_2 = float(price_2)

                break
            except ValueError:
                print("Invalid price. Must be a number.")

        print("Category information updated successfully!")

    def update_books_in_category(self):
        """Update books in a category (DI level)"""
        print("\nUpdate Books in Category")

        # Find category
        category = None
        while not category:
            search = input("Enter category ID or name: ").strip()
            category = self.records.find_book_category(search)
            if not category:
                print("Category not found. Try again or press Enter to cancel.")
                if not search:
                    return

        # Display current books
        print("\nCurrent books in category:")
        for book in category.books:
            print(f"- {book.name} ({book.id})")

        # Get action
        while True:
            action = input("\nAdd or remove books? (a/r/cancel): ").strip().lower()
            if action in ['a', 'add']:
                self.add_books_to_category(category)
                break
            elif action in ['r', 'remove']:
                self.remove_books_from_category(category)
                break
            elif action in ['c', 'cancel']:
                return
            else:
                print("Invalid choice. Enter 'a' to add, 'r' to remove, or 'c' to cancel.")

    def add_books_to_category(self, category):
        """Helper to add books to category"""
        print("\nEnter book IDs or names to add (comma separated):")
        book_input = input("Books: ").strip()
        if not book_input:
            print("No input provided.")
            return

        added = 0
        for book_id in [b.strip() for b in book_input.split(',')]:
            book = self.records.find_book(book_id)
            if book is None:
                print(f"Book '{book_id}' not found.")
            elif book in category.books:
                print(f"Book '{book.name}' is already in category '{category.name}'.")
            else:
                # Remove from previous category if needed
                if book.category:
                    book.category.remove_book(book)

                category.add_book(book)
                added += 1
                print(f"Added '{book.name}' to category '{category.name}'.")

        print(f"Added {added} books to category {category.name}")

    def remove_books_from_category(self, category):
        """Helper to remove books from category"""
        print("\nEnter book IDs or names to remove (comma separated):")
        book_input = input("Books: ").strip()
        if not book_input:
            return

        removed = 0
        for book_id in [b.strip() for b in book_input.split(',')]:
            book = self.records.find_book(book_id)
            if book and book in category.books:
                category.remove_book(book)
                removed += 1
            else:
                print(f"Book {book_id} not found in category")

        print(f"Removed {removed} books from category {category.name}")

    def adjust_member_discount(self):
        """Adjust discount rate for all members (DI level)"""
        print("\nAdjust Discount Rate for All Members")

        while True:
            try:
                rate = input("Enter new discount rate (e.g., 0.2 for 20%): ").strip()
                if not rate:
                    return

                rate = float(rate)
                if rate <= 0 or rate >= 1:
                    print("Rate must be between 0 and 1 (exclusive)")
                    continue

                Member.set_discount_rate(rate)
                GoldMember.set_discount_rate(rate)
                print(f"Discount rate updated to {rate*100:.0f}% for all members")
                break
            except ValueError:
                print("Invalid rate. Must be a number (e.g., 0.2 for 20%)")



    def adjust_gold_reward_rate(self):
        """Adjust reward rate for a Gold member (DI level)"""
        print("\nAdjust Reward Rate for Gold Member")

        # Find Gold member
        member = None
        while not member:
            search = input("Enter Gold member ID or name: ").strip()
            if not search:
                return

            customer = self.records.find_customer(search)
            if isinstance(customer, GoldMember):
                member = customer
            elif customer:
                print("This customer is not a Gold member")
            else:
                print("Customer not found. Try again or press Enter to cancel.")

        # Display current rate
        print(f"\nCurrent reward rate for {member.name}: {member.reward_rate*100:.0f}%")

        # Get new rate
        while True:
            try:
                rate = input("Enter new reward rate (e.g., 1 for 100%): ").strip()
                if not rate:
                    return

                rate = float(rate)
                if rate <= 0:
                    print("Rate must be positive")
                    continue

                member.set_reward_rate(rate)
                print(f"Reward rate updated to {rate*100:.0f}% for {member.name}")
                break
            except ValueError:
                print("Invalid rate. Must be a number (e.g., 1 for 100%)")

    def rent_books_via_file(self):
        """Process rentals from a file (HD level)"""
        filename = input("\nEnter rental file name: ").strip()
        if not filename:
            return

        self.records.process_rental_file(filename)

    def display_all_rentals(self):
        """Display all rental history (HD level)"""
        if not self.records.rentals:
            print("\nNo rentals found")
            return

        print("\nAll Rentals:")
        print("-" * 80)
        for rental in self.records.rentals:
            print(f"Date: {rental.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"Customer: {rental.customer.name} ({rental.customer.id})")
            print("Books:")
            for book, days in rental.books_and_days:
                print(f"- {book.name} for {days} days")
            print(f"Original Cost: {rental.original_cost:.2f} AUD")
            print(f"Discount: {rental.discount:.2f} AUD")
            print(f"Total Cost: {rental.total_cost:.2f} AUD")
            if isinstance(rental.customer, GoldMember):
                print(f"Reward Earned: {rental.reward}")
            print("-" * 80)

    def display_most_valuable_customer(self):
        customer = self.records.get_most_valuable_customer()
        if not customer:
            print("\nNo rentals found to determine valuable customer")
            return

        # Calculate total spending
        total = sum(r.total_cost for r in self.records._customer_rentals.get(customer.id, []))

        print("\nMost Valuable Customer:")
        print("-" * 40)
        customer.display_info()
        print(f"Total Spending: {total:.2f} AUD")
        print("-" * 40)

    def display_customer_rental_history(self):
        """Display rental history for a customer (HD level)"""
        customer = None
        while not customer:
            search = input("\nEnter customer ID or name: ").strip()
            if not search:
                return

            customer = self.records.find_customer(search)

            if not customer:
                print("Customer not found. Try again or press Enter to cancel.")
                return

        history = self.records.get_customer_rental_history(customer.id)
        if not history:
            print(f"\nNo rental history found for {customer.name}")
            return

        print(f"\nRental History for {customer.name}:")
        print("-" * 100)
        print(f"{'Rental':<10} | {'Books & Borrowing Days':<40} | {'Original Cost':<12} | "
              f"{'Discount':<10} | {'Final Cost':<10} | {'Rewards':<8}")
        print("-" * 100)

        for rental in history:
            print(f"{rental['rental_num']:<10} | {rental['books_info'][:40]:<40} | "
                  f"{rental['original_cost']:<12.2f} | {rental['discount']:<10.2f} | "
                  f"{rental['total_cost']:<10.2f} | {rental['reward']:<8}")
        print("-" * 100)

    def display_menu(self):
        #Display Menu
        print("\nBook Rental System Menu")
        print("1. Rent a book")
        print("2. Display existing customers")
        print("3. Display existing book categories")
        print("4. Display existing books")
        print("5. Update information of a book category")
        print("6. Update books of a book category")
        print("7. Adjust the discount rate of all members")
        print("8. Adjust the reward rate of a Gold member")
        print("9. Rent books via a file")
        print("10. Display all rentals")
        print("11. Display the most valuable customer")
        print("12. Display a customer rental history")
        print("13. Exit")


    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-13): ")

            try:
                if choice == '1':
                    self.rent_book()
                elif choice == '2':
                    self.records.list_customers()
                elif choice == '3':
                    self.records.list_book_categories()
                elif choice == '4':
                    self.records.list_books()
                elif choice == '5':
                    self.update_book_category()
                elif choice == '6':
                    self.update_books_in_category()
                elif choice == '7':
                    self.adjust_member_discount()
                elif choice == '8':
                    self.adjust_gold_reward_rate()
                elif choice == '9':
                    self.rent_books_via_file()
                elif choice == '10':
                    self.display_all_rentals()
                elif choice == '11':
                    self.display_most_valuable_customer()
                elif choice == '12':
                    self.display_customer_rental_history()
                elif choice == '13':
                    # Save data before exiting
                    self.records.save_data("customers.txt", "books.txt", "book_categories.txt", "rentals.txt")
                    print("Thank you for using the Book Rental System. Goodbye!")
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 13.")
            except Exception as e:
                print(f"An error occurred: {e}")

# Main Program
if __name__ == "__main__":
    try:
        system = Operations()
        system.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Saving data...")
        system.records.save_data("customers.txt", "books.txt", "book_categories.txt", "rentals.txt")
        print("Goodbye!")
    except Exception as e:
        print("Fatal error:")
        traceback.print_exc()  # ✅ Shows full stack trace
        sys.exit(1)
