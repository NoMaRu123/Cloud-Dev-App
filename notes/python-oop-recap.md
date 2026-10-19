# Python OOP recap

A refresher on the four object-oriented ideas, written for Python. They exist in almost every object-oriented language (Java, C#, JavaScript, PHP), and Python has all four with less ceremony. Every example below was run with Python 3.12, and the outputs shown are real.

## 1. Classes and objects

A class is a blueprint. An object is one thing built from it. `__init__` runs when an object is created, and `self` is the object itself (Java's `this`, except Python makes you write it as the first parameter of every method).

```python
class Account:
    bank_name = "NCI Bank"              # class attribute: ONE value shared by every Account

    def __init__(self, owner, balance=0):
        self.owner = owner              # instance attributes: each object has its own
        self.balance = balance

    def deposit(self, amount):          # a method: a function that belongs to the class
        self.balance += amount

acc = Account("Alex")                   # creates the object; __init__ runs
acc.deposit(50)
print(acc.owner, acc.balance, acc.bank_name)
```
Output: `Alex 50 NCI Bank`

- Attributes set on `self` inside `__init__` belong to that one object. Attributes written directly in the class body are shared by all objects (see the first trap below).
- Python has no `private` keyword. A leading underscore (`self._state`) is a convention meaning "internal, don't touch from outside".

## 2. Inheritance

A child class gets everything from its parent, can add more, and can override methods.

```python
class SavingsAccount(Account):              # SavingsAccount inherits from Account
    def __init__(self, owner, balance=0, rate=0.02):
        super().__init__(owner, balance)     # run the parent's __init__ first
        self.rate = rate

    def add_interest(self):
        self.deposit(self.balance * self.rate)   # reuses the parent's deposit()

sav = SavingsAccount("Sam", 1000)
sav.add_interest()
print(sav.balance, isinstance(sav, Account), isinstance(acc, SavingsAccount))
```
Output: `1020.0 True False`

- `super().__init__(...)` calls the parent's constructor. If you forget it, the parent's attributes (`owner`, `balance`) never get set.
- A `SavingsAccount` is an `Account` (`True`), but a plain `Account` is not a `SavingsAccount` (`False`).

## 3. Abstract classes (Python's interfaces)

An abstract class is a contract: it lists methods that every subclass must have. Python does this with `ABC` and `@abstractmethod`.

```python
from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, message):        # every Notifier must have send()
        pass

class EmailNotifier(Notifier):
    def send(self, message):
        print(f"Email: {message}")

class SmsNotifier(Notifier):
    def send(self, message):
        print(f"SMS: {message}")
```

You can't create the abstract class itself, or a subclass that forgot the method:

```python
Notifier()
# TypeError: Can't instantiate abstract class Notifier without an implementation for abstract method 'send'

class BrokenNotifier(Notifier):
    pass

BrokenNotifier()
# TypeError: Can't instantiate abstract class BrokenNotifier without an implementation for abstract method 'send'
```

The error appears when the object is created, before any code tries to call the missing method. That early warning is the main reason to use an ABC.

## 4. Polymorphism

The same method name on different classes, each doing its own thing. The calling code doesn't care which class it has.

```python
notifiers = [EmailNotifier(), SmsNotifier()]
for n in notifiers:
    n.send("You are over budget")
```
Output:
```
Email: You are over budget
SMS: You are over budget
```

Python goes further than Java here. It doesn't check the parent class at all, only whether the method exists. This is called duck typing ("if it walks like a duck and quacks like a duck...").

```python
class Pigeon:                         # no Notifier parent at all
    def send(self, message):
        print(f"Pigeon: {message}")

for n in [EmailNotifier(), Pigeon()]:
    n.send("Hello")
```
Output:
```
Email: Hello
Pigeon: Hello
```

So in Python an ABC is optional for polymorphism. It's still worth using when you want the contract written down and mistakes caught early, which is why `observer.py` uses one.

## Python next to Java

| | Java | Python |
|---|---|---|
| The current object | `this` (implicit) | `self` (written as the first parameter) |
| Constructor | a method named after the class | `__init__` |
| Calling the parent | `super(...)` | `super().__init__(...)` |
| Interface | `interface`, `implements` | `ABC` + `@abstractmethod` (optional) |
| Private | `private` keyword | `_name` by convention |
| Types | required | optional hints (`amount: float`, `-> None`) |
| Polymorphism needs a shared parent? | yes (class or interface) | no, duck typing is enough |
| Overloading (same name, different parameters) | yes | no, use default values instead |

## Where you've already used these

| In your lab code | Idea |
|---|---|
| `class Item(BaseModel)` in `schemas.py` | inheritance: Pydantic's `BaseModel` gives your class validation |
| `class Item(Base)` in `models.py` | inheritance: SQLAlchemy's `Base` turns your class into a table |
| `class UnitTests(unittest.TestCase)` | inheritance: you get `assertEqual` and friends for free |
| `raise HTTPException(status_code=404, ...)` | creating an object from a class, then raising it |
| `SingletonMeta.__call__` | overriding a special method to change what `Singleton()` does |
| `observer.update(self)` in a loop | polymorphism: one loop, any kind of observer |

## Two traps worth remembering

### A list in the class body is shared by every object

```python
class Subject:
    _observers = []                  # class level: ONE list shared by all Subjects
    def attach(self, o):
        self._observers.append(o)

s1, s2 = Subject(), Subject()
s1.attach("A")
print("s2 sees:", s2._observers)
```
Output: `s2 sees: ['A']`. Attaching to `s1` also changed `s2`.

The fix is to create the list in `__init__`, so each object gets its own:

```python
class FixedSubject:
    def __init__(self):
        self._observers = []         # created per object
    def attach(self, o):
        self._observers.append(o)

f1, f2 = FixedSubject(), FixedSubject()
f1.attach("A")
print("f2 sees:", f2._observers)
```
Output: `f2 sees: []`

The lecturer's `observer.py` has this exact trap (`_observers: List[Observer] = []` in the class body). It doesn't show there because the example only creates one subject.

### A list as a default argument is shared between calls

```python
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags

print(add_tag("food"), add_tag("rent"))
```
Output: `['food', 'rent'] ['food', 'rent']`. The second call still had "food", because the default list is created once, when the function is defined.

```python
def add_tag_fixed(tag, tags=None):
    if tags is None:
        tags = []                    # a new list on every call
    tags.append(tag)
    return tags

print(add_tag_fixed("food"), add_tag_fixed("rent"))
```
Output: `['food'] ['rent']`

Both traps come from the same rule: a list created once is the same list everywhere it's used.

## Check yourself

1. What's the difference between `bank_name` and `self.balance` in `Account`?
2. What happens if `SavingsAccount.__init__` forgets `super().__init__(owner, balance)`?
3. Why does `Notifier()` raise a `TypeError`, and when exactly does it happen?
4. `Pigeon` doesn't inherit from `Notifier`. Why does the loop still work?

Answers:

1. `bank_name` is a class attribute shared by every account. `self.balance` belongs to one object.
2. `owner` and `balance` are never set, so `deposit` fails with an `AttributeError`.
3. It has an abstract method with no implementation, so Python refuses to create it, at the moment of creation rather than when `send` is called.
4. Duck typing: Python only checks that `send` exists, not which class the object comes from.
