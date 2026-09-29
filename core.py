"""花店核心逻辑：订单、冷库、花材和计费。"""

import json


def new_game():
    return {
        "orders": {},
        "cold_load": 0,
        "cold_capacity": 2,
        "flowers": 100,
        "day": 1,
        "order_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    return state


def create_order(state, order_id, member=False):
    if order_id in state["orders"]:
        return False
    state["orders"][order_id] = {"member": member}
    return True


def store(state, order_id, amount):
    if state["cold_load"] + amount > state["cold_capacity"]:
        return False
    state["cold_load"] += amount
    state["flowers"] -= amount
    order = state["orders"].setdefault(order_id, {"member": False})
    order["stored"] = order.get("stored", 0) + amount
    return True


def fee(state, order_id, end_day):
    return end_day - state["day"]


def cancel_order(state, order_id, amount):
    order = state["orders"].get(order_id, {})
    refund = min(amount, order.get("stored", 0))
    state["flowers"] += refund
    state["cold_load"] = max(0, state["cold_load"] - refund)
    state["orders"].pop(order_id, None)
    return True


def discount(state, order_id, base):
    if state["orders"][order_id]["member"]:
        return base - 10
    return base


def deliver(state, order_id, paid):
    order = state["orders"].get(order_id)
    if order is None:
        return False
    if not paid:
        return False
    if order.get("settled"):
        return False
    order["settled"] = True
    return True


def reserve(state, order_id, days):
    state.setdefault("slots", {})[order_id] = state["day"] + days
    return True


def expire(state, current_day):
    for slot, day in state.get("slots", {}).items():
        if day is not None and current_day > day:
            state["slots"][slot] = None
    return True


def main():
    print("花店 - 命令: order/store/fee/cancel/discount/deliver/reserve/expire/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
