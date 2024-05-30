from collections import UserDict
from datetime import datetime, date, timedelta
import pickle


def find_next_weekday(current_date, target_weekday):
    days_ahead = target_weekday - current_date.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return current_date + timedelta(days=days_ahead)



def adjust_birthday(birthday):
    if birthday.weekday() == 5:
        return find_next_weekday(birthday, 1) 
    elif birthday.weekday() == 6: 
        return find_next_weekday(birthday, 2)  
    else:
        return birthday 


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Invalid input. Please check your input format and try again."
        except KeyError:
            return "Invalid input. The specified key does not exist."
        except IndexError:
            return "Invalid input. Please provide all necessary arguments."
    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

class Field:
    def __init__(self, value):
        self.value = value
        self.validate()

    def __str__(self):
        return str(self.value)

class Name(Field):
    def validate(self):
        if not isinstance(self.value, str):
            raise ValueError("Name must be a string")

class Phone(Field):
    def validate(self):
        if not isinstance(self.value, str):
            raise ValueError("Phone number must be a string")
        if not self.value.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(self.value) != 10:
            raise ValueError("Phone number must be 10 digits long")

class Birthday(Field):
    def validate(self):
        try:
            datetime.strptime(self.value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Please use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def get_phone(self):
        return "; ".join(str(phone) for phone in self.phones)

    

    def change_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)
    

    def add_birthday(self, birthday):
        birthday_date = datetime.strptime(birthday, "%d.%m.%Y").date()
        adjusted_birthday = adjust_birthday(birthday_date)
        self.birthday = Birthday(adjusted_birthday.strftime("%d.%m.%Y"))

    def show_birthday(self):
        return str(self.birthday) if self.birthday else "Birthday not set"


    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

 
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = date.today()
        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_date = birthday_date.replace(year=today.year)
                if birthday_date < today:
                    birthday_date = birthday_date.replace(year=today.year + 1)
                upcoming_birthdays.append({"name": record.name.value, "birthday": birthday_date})
        return upcoming_birthdays


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        print("Upcoming birthdays within the next week:")
        for user in upcoming_birthdays:
            birthday = user['birthday']
            if birthday.weekday() >= 5:
                birthday = find_next_weekday(birthday, 0)
            print(f"{user['name']}: {birthday.strftime('%d.%m.%Y')}")
    else:
        print("No upcoming birthdays within the next week.")

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}"
    else:
        return "Contact not found"

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record:
        return record.show_birthday()
    else:
        return "Contact not found"

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact update."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_phone(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.change_phone(old_phone, new_phone)
        return f"Phone number changed for {name}"
    else:
        return "Contact not found"


@input_error
def get_phone(self, name):
    record = self.find(name)
    if record:
        return record.get_phone()
    else:
        return "Contact not found"


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    try:
        while True:
            user_input = input("Enter a command: ")
            command, *args = parse_input(user_input)

            if command in ["close", "exit"]:
                print("Good bye!")
                break

            elif command == "hello":
                print("How can I help you?")

            elif command == "add":
                print(add_contact(args, book))

            elif command == "change":
                print(change_phone(args, book))

            elif command == "phone":
                if not args:
                    print("Please provide the name of the contact.")
                    continue
                name, *_ = args
                record = book.find(name)
                if record:
                    phone_numbers = record.get_phone()
                    print(phone_numbers)
                else:
                    print("Contact not found")

            elif command == "all":
                for record in book.data.values():
                    print(record)

            elif command == "add-birthday":
                print(add_birthday(args, book))

            elif command == "show-birthday":
                print(show_birthday(args, book))

            elif command == "birthdays":
                birthdays(args, book)

            else:
                print("Invalid command.")

    finally:
        save_data(book)


if __name__ == "__main__":
    main()

