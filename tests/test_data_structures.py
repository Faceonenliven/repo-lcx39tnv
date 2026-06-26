"""Comprehensive tests for the data_structures module."""

import pytest

from src.data_structures import LinkedList, Queue, Stack


class TestStack:
    def test_new_stack_is_empty(self):
        s = Stack()
        assert s.is_empty() is True
        assert s.size() == 0

    def test_push_single(self):
        s = Stack()
        s.push(1)
        assert s.is_empty() is False
        assert s.size() == 1

    def test_push_multiple(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.push(3)
        assert s.size() == 3

    def test_pop_returns_last_pushed(self):
        s = Stack()
        s.push("a")
        s.push("b")
        assert s.pop() == "b"
        assert s.pop() == "a"

    def test_pop_empty_raises(self):
        s = Stack()
        with pytest.raises(IndexError, match="empty stack"):
            s.pop()

    def test_peek_returns_top(self):
        s = Stack()
        s.push(10)
        s.push(20)
        assert s.peek() == 20
        assert s.size() == 2  # peek doesn't remove

    def test_peek_empty_raises(self):
        s = Stack()
        with pytest.raises(IndexError, match="empty stack"):
            s.peek()

    def test_lifo_order(self):
        s = Stack()
        for i in range(5):
            s.push(i)
        result = []
        while not s.is_empty():
            result.append(s.pop())
        assert result == [4, 3, 2, 1, 0]


class TestQueue:
    def test_new_queue_is_empty(self):
        q = Queue()
        assert q.is_empty() is True
        assert q.size() == 0

    def test_enqueue_single(self):
        q = Queue()
        q.enqueue(1)
        assert q.is_empty() is False
        assert q.size() == 1

    def test_enqueue_multiple(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        assert q.size() == 3

    def test_dequeue_returns_first_enqueued(self):
        q = Queue()
        q.enqueue("a")
        q.enqueue("b")
        assert q.dequeue() == "a"
        assert q.dequeue() == "b"

    def test_dequeue_empty_raises(self):
        q = Queue()
        with pytest.raises(IndexError, match="empty queue"):
            q.dequeue()

    def test_front_returns_first(self):
        q = Queue()
        q.enqueue(10)
        q.enqueue(20)
        assert q.front() == 10
        assert q.size() == 2  # front doesn't remove

    def test_front_empty_raises(self):
        q = Queue()
        with pytest.raises(IndexError, match="empty queue"):
            q.front()

    def test_fifo_order(self):
        q = Queue()
        for i in range(5):
            q.enqueue(i)
        result = []
        while not q.is_empty():
            result.append(q.dequeue())
        assert result == [0, 1, 2, 3, 4]


class TestLinkedList:
    def test_new_list_is_empty(self):
        ll = LinkedList()
        assert ll.is_empty() is True
        assert ll.size() == 0

    def test_append_single(self):
        ll = LinkedList()
        ll.append(1)
        assert ll.size() == 1
        assert ll.to_list() == [1]

    def test_append_multiple(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert ll.to_list() == [1, 2, 3]

    def test_prepend_single(self):
        ll = LinkedList()
        ll.prepend(1)
        assert ll.size() == 1
        assert ll.to_list() == [1]

    def test_prepend_multiple(self):
        ll = LinkedList()
        ll.prepend(1)
        ll.prepend(2)
        ll.prepend(3)
        assert ll.to_list() == [3, 2, 1]

    def test_append_and_prepend(self):
        ll = LinkedList()
        ll.append(2)
        ll.prepend(1)
        ll.append(3)
        assert ll.to_list() == [1, 2, 3]

    def test_delete_head(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        ll.delete(1)
        assert ll.to_list() == [2, 3]
        assert ll.size() == 2

    def test_delete_middle(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        ll.delete(2)
        assert ll.to_list() == [1, 3]

    def test_delete_tail(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        ll.delete(3)
        assert ll.to_list() == [1, 2]

    def test_delete_not_found(self):
        ll = LinkedList()
        ll.append(1)
        with pytest.raises(ValueError, match="not found"):
            ll.delete(99)

    def test_delete_from_empty(self):
        ll = LinkedList()
        with pytest.raises(ValueError, match="not found"):
            ll.delete(1)

    def test_find_existing(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        node = ll.find(2)
        assert node is not None
        assert node.data == 2

    def test_find_not_existing(self):
        ll = LinkedList()
        ll.append(1)
        assert ll.find(99) is None

    def test_find_in_empty(self):
        ll = LinkedList()
        assert ll.find(1) is None

    def test_is_empty_after_operations(self):
        ll = LinkedList()
        ll.append(1)
        ll.delete(1)
        assert ll.is_empty() is True

    def test_to_list_empty(self):
        ll = LinkedList()
        assert ll.to_list() == []
