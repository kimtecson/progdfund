class Customer:
    def __init__(self, id, name):
        self.__id = id
        self.__name = name

    @property
    def get_id(self):
        return self.id

    @property
    def get_name(self):
        return self.name

    def display_info(self):
        print(f"Customer ID: {self.id}, Name: {self.name}")


class Member(Customer):
    __discount_rate = 0.10

    def __init__(self, id, name):
        super().__init__(id, name)

    def get_discount_rate(self):
        return Member.__discount_rate

    def get_discount(self, rental_cost):
        return rental_cost * Member.__discount_rate

    def display_info(self):
        print(f"Member ID: {self.id}, Name: {self.name}, Discount Rate: {Member.__discount_rate * 100:.0f}%")

    @staticmethod
    def set_discount_rate(new_rate):
        Member.__discount_rate = new_rate


class GoldMember(Member):
    __discount_rate = 0.12

    def __init__(self, ID, name, reward_rate=1.0):
        super().__init__(ID, name)
        self.reward_rate = reward_rate
        self.reward = 0

    def get_reward_rate(self):
        return self.reward_rate

    def get_discount(self, rental_cost):
        return rental_cost * GoldMember.__discount_rate

    def get_reward(self, rental_cost):
        discounted_cost = rental_cost - self.get_discount(rental_cost)
        return round(discounted_cost * self.reward_rate)

    def update_reward(self, value):
        self.reward += value

    def display_info(self):
        print(
            f"GoldMember ID: {self.id}, Name: {self.name}, "
            f"Discount Rate: {GoldMember.__discount_rate * 100:.0f}%, "
            f"Reward Rate: {self.reward_rate * 100:.0f}%, "
            f"Reward: {self.reward}"
        )

    @staticmethod
    def set_discount_rate(new_rate):
        GoldMember.__discount_rate = new_rate

    def set_reward_rate(self, new_rate):
        self.reward_rate = new_rate

class Book:
    def __init__(self, ID, name, category):
        self.id = ID
        self.name = name
        self.category = category

    def get_name(self):
        return self.name

    def get_category(self):
        return self.category

    def display_info(self):
        print(f"Book ID: {self.id}, Name: {self.name}, Category: {self.category.get_name() if isinstance(self.category, BookCategory) else self.category}")

    def get_price(self, days):
        if isinstance(self.category, BookCategory):
            return self.category.get_price(days)
        else:
            return None

class BookCategory:
    def __init__(self, ID, name, price_1, price_2):
        self.id = ID
        self.name = name
        self.price_1 = price_1
        self.price_2 = price_2
        self.books = []

    def get_price(self, days):
        if days <= 3:
            return days * self.price_1
        else:
            return (3 * self.price_1) + ((days - 3) * self.price_2)

    def add_book(self, book):
        self.books.append(book)

    def display_info(self):
        print(f"BookCategory ID: {self.id}, Name: {self.name}, Price-1: {self.price_1}, Price-2: {self.price_2}")
        print("Books in this category:")
        for book in self.books:
            print(f"- {book.get_name()} (ID: {book.get_id()})")

class Rental:
    def __init__(self, customer, book, borrowing_days):

        self.__customer = customer
        self.book = book
        self.borrowing_days = borrowing_days

    @property
    def customer(self):
        return self.__customer

    @customer.setter
    def customer(self, value):
        self.__customer = value

    @property
    def book(self):
        return self.book

    @book.setter
    def book(self, value):
        self.book = value

    @property
    def borrowing_days(self):
        return self.borrowing_days

    @borrowing_days.setter
    def borrowing_days(self, value):
        # Check that value is a positive integer
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Borrowing days must be a positive integer")
        self._borrowing_days = value

    def compute_cost(self):
        if not isinstance(self.book.category, BookCategory):
            raise ValueError("Book must have a valid BookCategory to calculate price")
        original_cost = self.book.daily_rate * self.borrowing_days

        # Calculate discount if customer has discount_rate attribute
        discount = 0
        if hasattr(self.__customer, 'discount_rate'):
            discount = original_cost * self.__customer.discount_rate

        # Calculate discount based on customer type
        if isinstance(self.__customer, Member):
            discount = self.__customer.get_discount(original_cost)
        elif isinstance(self.__customer, GoldMember):
            discount = self.__customer.get_discount(original_cost)
        else:  # Regular Customer
            discount = 0

        total_cost = original_cost - discount

        # For Gold members
        if isinstance(self.__customer, GoldMember):
            reward = self.__customer.get_reward(original_cost)
            self.__customer.update_reward(reward)  # Update the customer's reward points
            return (original_cost, discount, total_cost, reward)

        return (original_cost, discount, total_cost)

class Records:
    def __init__(self):
        self.__customers = []
        self.books = []
        self.book_categories = []

    def read_customers(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(', ')
                customer_type, id, name, discount_rate, reward_rate, reward = parts
                if customer_type == "C":
                    self.__customers.append(Customer(id, name))
                elif customer_type == "M":
                    member = Member(id, name)
                    if discount_rate != "na":
                        member.set_discount_rate(float(discount_rate))
                    self.__customers.append(member)
                elif customer_type == "G":
                    gm = GoldMember(id, name, float(reward_rate))
                    if discount_rate != "na":
                        gm.set_discount_rate(float(discount_rate))
                    if reward != "na":
                        gm.update_reward(int(reward))
                    self.__customers.append(gm)

    def read_books_and_book_categories(self, book_file, category_file):
        book_dict = {}
        with open(book_file, 'r') as file:
            for line in file:
                book_id, book_name = line.strip().split(', ')
                book_dict[book_id] = Book(book_id, book_name, None)
                self.books.append(book_dict[book_id])

        with open(category_file, 'r') as file:
            for line in file:
                parts = line.strip().split(', ')
                cat_id, cat_name = parts[0], parts[1]
                price1, price2 = float(parts[2]), float(parts[3])
                book_ids = parts[4:]
                category = BookCategory(cat_id, cat_name, price1, price2)
                for book_id in book_ids:
                    book = book_dict.get(book_id)
                    if book:
                        book.category = category
                        category.add_book(book)
                self.book_categories.append(category)
