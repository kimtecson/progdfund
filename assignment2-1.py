class Customer:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @property
    def id(self):
        return self.id

    @property
    def name(self):
        return self.name

    def display(self):
        print(f"ID: {self.id}, Name: {self.name}")

class Member(Customer):
    discount_rate = .10

    def __init__(self, id, name):
        super().__init__(id, name)

    @property
    def discount_rate(self):
        return self.discount_rate

    def get_discount(self, rental_cost):
        return rental_cost * Member.discount_rate

    def display_info(self):
        print (f"ID: {self.id}, Name: {self.name}, {self.discount_rate}")

    @staticmethod
    def set_discount_rate(new_rate):
        Member.discount_rate = new_rate

class GoldMember(Member):
    discount_rate = 0.12

    def __init__(self, ID, name, reward_rate=1.0):
        super().__init__(ID, name)
        self.reward_rate = reward_rate
        self.reward = 0

    @property
    def reward_rate(self):
        return self.reward_rate

    def get_reward_rate(self):
        return self.reward_rate

    def get_discount(self, rental_cost):
        return rental_cost * GoldMember.discount_rate #self.discount or GoldM?

    def get_reward(self, rental_cost):
        discounted_cost = rental_cost - self.get_discount(rental_cost)
        return round(discounted_cost * self.reward_rate)

    def update_reward(self, new_reward):
        self.reward += new_reward

    def display_info(self):
        print(
            f"GoldMember ID: {self.id}, Name: {self.name}, "
            f"Discount Rate: {GoldMember.discount_rate * 100:.0f}%, "
            f"Reward Rate: {self.reward_rate * 100:.0f}%, "
            f"Reward: {self.reward}"
        )

    @staticmethod
    def set_discount_rate(new_rate):
        GoldMember.discount_rate = new_rate

    def set_reward_rate(self, new_reward_rate):
        self.reward_rate = new_reward_rate

class Book:
    def __init__(self, id, name, category, base_price):
        self.id = id
        self.name = name #assume the book names are unique and they do not include any digit
        self.category = category
        self.base_price  = base_price
        self.is_available = True  # Additional attribute to track availability


    @property
    def id(self):
        return self.id

    @property
    def name(self):
        return self.name

    @property
    def category(self):
        return self.category

    @property
    def is_available(self):
        return self.is_available

    def display_info(self):
        """Prints all book information"""
        print(f"Book ID: {self.id}")
        print(f"Book Name: {self.name}")
        print(f"Category: {self.category}")
        print(f"Daily Rental Price: ${self.base_price:.2f}")
        print(f"Availability: {'Available' if self.is_available else 'Rented'}")

    def get_rental_price(self, borrowing_days):
        return self.category.get_price(borrowing_days)  # Delegate to BookCategory

    def rent(self):
        #Marks the book as rented
        if not self.is_available:
            raise Exception("Book is already rented")
        self.is_available = False

    def return_book(self):
        #Marks the book as available
        self.is_available = True

    def set_base_price(self, new_price):

        if new_price <= 0:
            raise ValueError("Price must be positive")
        self.base_price = new_price

class BookCategory:
    def __init__(self, category_id, category_name, price_1, price_2):
        self.id = category_id
        self.category_name = category_name #assume the book category names are unique and they do not include any digit
        self.price_1 = price_1
        self.price_2 = price_2
        self.books = [] # List to store Book objects

    @property
    def id(self):
        return self.id

    @property
    def category_name(self):
        return self.category_name

    @property
    def price_1(self):
        return self.price_1

    @property
    def price_2(self):
        return self.price_2

    @property
    def books(self):
        return self.books #books copy?

    def display_info(self):
        """Prints all category information"""
        print(f"Category ID: {self.id}")
        print(f"Category Name: {self.name}")
        print(f"First-tier Price: ${self.price_1:.2f}/day")
        print(f"Second-tier Price: ${self.price_2:.2f}/day")
        print(f"Number of Books: {len(self.books)}")

    def add_book(self, book):
        if not isinstance(book, Book):
            raise TypeError("Can only add Book objects to category")
        self.books.append(book)

    def get_price(self, borrowing_days):
        if borrowing_days <= 0:
            raise ValueError("Number of days must be positive")

        # Example tiered pricing logic (can be customized):
        # - First 7 days at price_1
        # - Additional days at price_2
        tier1_days = min(borrowing_days, 7)
        tier2_days = max(borrowing_days - 7, 0)
        return (tier1_days * self.price_1) + (tier2_days * self.price_2)

    def remove_book(self, book):
        if book in self.books:
            self.books.remove(book)

    def update_prices(self, new_price_1, new_price_2):
        if new_price_1 <= 0 or new_price_2 <= 0:
            raise ValueError("Prices must be positive")
        self.price_1 = new_price_1
        self.price_2 = new_price_2

class Rental:

    def __init__(self, customer, book, borrowing_days):
        if not isinstance(customer, (Customer, Member, GoldMember)):
            raise TypeError("Customer must be a Customer, Member, or GoldMember")
        if not isinstance(book, Book):
            raise TypeError("Book must be a Book object")
        if borrowing_days <= 0:
            raise ValueError("Borrowing days must be positive")

        self.customer = customer
        self.book = book
        self.borrowing_days = borrowing_days
        self.is_returned = False  # Additional attribute to track rental status

        @property
        def customer(self):
            return self.customer

        @property
        def book(self):
            return self.book

        @property
        def borrowing_days(self):
            return self.borrowing_days

        @property
        def is_returned(self):
            return self.is_returned

        def compute_cost(self):
            original_cost = self.book.get_price(self.borrowing_days)
            discount = 0.0
            reward = 0

        if isinstance(self.customer, (Member, GoldMember)):
            discount = self.customer.get_discount(original_cost)
            total_cost = original_cost - discount
        else:
            total_cost = original_cost

        if isinstance(self.customer, GoldMember):
            reward = self.customer.get_reward(total_cost)

        # Mark book as rented when computing cost
        self.book.rent()

        if isinstance(self.customer, GoldMember):
            return (original_cost, discount, total_cost, reward)
        else:
            return (original_cost, discount, total_cost)

        def return_rental(self):
            if not self.is_returned:
                self.book.return_book()
                self.is_returned = True
                if isinstance(self.customer, GoldMember):
                    # Add reward points when returning (if GoldMember)
                    discounted_cost = self.book.get_price(self.borrowing_days) * \
                                    (1 - self.customer.discount_rate)
                    reward = self.customer.get_reward(discounted_cost)
                    self.customer.update_reward(reward)
            else:
                raise Exception("This rental has already been returned")

        def display_info(self):
            """Displays rental information"""
            print(f"Customer: {self.customer.name}")
            print(f"Book: {self.book.name}")
            print(f"Borrowing Days: {self.borrowing_days}")
            print(f"Status: {'Returned' if self.is_returned else 'Active'}")
            cost_info = self.compute_cost()
            if len(cost_info) == 4:
                print(f"Original Cost: ${cost_info[0]:.2f}")
                print(f"Discount: ${cost_info[1]:.2f}")
                print(f"Total Cost: ${cost_info[2]:.2f}")
                print(f"Reward Points Earned: {cost_info[3]}")
            else:
                print(f"Original Cost: ${cost_info[0]:.2f}")
                print(f"Discount: ${cost_info[1]:.2f}")
                print(f"Total Cost: ${cost_info[2]:.2f}")
