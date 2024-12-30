class Fastag:
    def __init__(self, tag_id, balance, vehicle_id):
        self.id = tag_id
        self.balance = balance
        self.status = "valid"
        self.vehicle_id = vehicle_id
        self.email = ""