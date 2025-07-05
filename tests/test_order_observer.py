from unittest.mock import MagicMock

from patterns.order_observer import Order


def test_finalize_notifies_observers():
    order = Order(1)
    observer1 = MagicMock(spec=["update"])
    observer2 = MagicMock(spec=["update"])
    order.register(observer1)
    order.register(observer2)

    order.finalize()

    observer1.update.assert_called_once_with(order)
    observer2.update.assert_called_once_with(order)
    assert order.finalized
