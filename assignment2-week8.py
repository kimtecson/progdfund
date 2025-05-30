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

    @id.setter
    def id(self, newId):
        self.__id = newId

    @name.setter
    def name(self, newName):
        self.__name = newName

    def display_info(self):
        print(f"Customer ID: {self.id}, Name: {self.name}")


class Member(Customer):
    discount_rate = 0.10

    def __init__(self, id, name):
        super().__init__(id, name)

    def get_discount_rate(self):
        return Member.discount_rate

    def get_discount(self, rental_cost):
        return rental_cost * Member.discount_rate

    def display_info(self):
        print(f"Member ID: {self.id}, Name: {self.name}, Discount Rate: {Member.discount_rate * 100:.0f}%")

    @staticmethod
    def set_discount_rate(new_rate):
        Member.discount_rate = new_rate


class GoldMember(Member):
    _discount_rate = 0.12

    def __init__(self, ID, name, reward_rate=1.0):
        super().__init__(ID, name)
        self.reward_rate = reward_rate
        self.reward = 0

    def get_reward_rate(self):
        return self.reward_rate

    def get_discount(self, rental_cost):
        return rental_cost * GoldMember.discount_rate

    def get_reward(self, rental_cost):
        discounted_cost = rental_cost - self.get_discount(rental_cost)
        return round(discounted_cost * self.reward_rate)

    def update_reward(self, value):
        self._reward += value

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
