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
        "stored": {},
        "slots": {},
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state.setdefault("orders", {})
    state.setdefault("stored", {})
    state.setdefault("slots", {})
    state.setdefault("cold_load", 0)
    state.setdefault("cold_capacity", 2)
    state.setdefault("flowers", 100)
    state.setdefault("day", 1)
    state.setdefault("order_id", 0)
    return state


def create_order(state, order_id, member=False):
    if order_id in state["orders"]:
        return False
    state["orders"][order_id] = {"member": member}
    return True


def store(state, order_id, amount):
    if amount <= 0:
        return False
    if state["cold_load"] + amount > state["cold_capacity"]:
        return False
    if amount > state["flowers"]:
        return False
    state["cold_load"] += amount
    state["flowers"] -= amount
    state["stored"][order_id] = state["stored"].get(order_id, 0) + amount
    return True


def fee(state, order_id, end_day):
    order = state["orders"].get(order_id)
    if order is not None:
        if order.get("settled"):
            return 0
        order["settled"] = True
    days = end_day - state["day"]
    return days if days > 0 else 0


def cancel_order(state, order_id, amount):
    order = state["orders"].get(order_id)
    if order is not None:
        if order.get("canceled"):
            return False
        order["canceled"] = True
    held = state["stored"].get(order_id, 0)
    refund = min(amount, held)
    if refund > 0:
        state["flowers"] += refund
        state["cold_load"] -= refund
        state["stored"][order_id] = held - refund
    return True


def discount(state, order_id, base):
    if state["orders"][order_id]["member"]:
        return base - 10
    return base


def deliver(state, order_id, paid):
    if not paid:
        return False
    order = state["orders"].get(order_id)
    if order is None or order.get("settled"):
        return False
    order["settled"] = True
    return True


def reserve(state, order_id, days):
    if days <= 0:
        return False
    for slot, holder in state["slots"].items():
        if holder is None:
            state["slots"][slot] = state["day"] + days
            return True
    used = [name for name in state["slots"] if name.startswith("S")]
    slot = "S" + str(len(used) + 1)
    while slot in state["slots"]:
        slot = "S" + str(int(slot[1:]) + 1)
    state["slots"][slot] = state["day"] + days
    return True


def expire(state, current_day):
    for slot, until in list(state["slots"].items()):
        if until is not None and current_day >= until:
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
