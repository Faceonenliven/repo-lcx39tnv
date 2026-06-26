"""Data structures module providing common data structure implementations."""


class Stack:
    """A simple stack implementation using a list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Push an item onto the stack."""
        self._items.append(item)

    def pop(self):
        """Pop an item from the stack. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("Peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        """Return True if the stack is empty."""
        return len(self._items) == 0

    def size(self):
        """Return the number of items in the stack."""
        return len(self._items)


class Queue:
    """A simple queue implementation using a list."""

    def __init__(self):
        self._items = []

    def enqueue(self, item):
        """Add an item to the end of the queue."""
        self._items.append(item)

    def dequeue(self):
        """Remove and return the front item. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("Dequeue from empty queue")
        return self._items.pop(0)

    def front(self):
        """Return the front item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("Front from empty queue")
        return self._items[0]

    def is_empty(self):
        """Return True if the queue is empty."""
        return len(self._items) == 0

    def size(self):
        """Return the number of items in the queue."""
        return len(self._items)


class LinkedListNode:
    """A node in a linked list."""

    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """A singly linked list implementation."""

    def __init__(self):
        self.head = None
        self._size = 0

    def append(self, data):
        """Append data to the end of the list."""
        new_node = LinkedListNode(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1

    def prepend(self, data):
        """Prepend data to the beginning of the list."""
        new_node = LinkedListNode(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def delete(self, data):
        """Delete the first occurrence of data. Raises ValueError if not found."""
        if self.head is None:
            raise ValueError(f"Value {data} not found in list")
        if self.head.data == data:
            self.head = self.head.next
            self._size -= 1
            return
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self._size -= 1
                return
            current = current.next
        raise ValueError(f"Value {data} not found in list")

    def find(self, data):
        """Find the first node containing data. Returns None if not found."""
        current = self.head
        while current:
            if current.data == data:
                return current
            current = current.next
        return None

    def to_list(self):
        """Convert linked list to a Python list."""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def size(self):
        """Return the number of elements in the list."""
        return self._size

    def is_empty(self):
        """Return True if the list is empty."""
        return self._size == 0
