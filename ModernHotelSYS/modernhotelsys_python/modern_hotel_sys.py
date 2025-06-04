import csv
import datetime
import os

class Room:
    def __init__(self, room_number, room_type, price_per_night):
        self.room_number = room_number
        self.room_type = room_type
        self.price_per_night = price_per_night

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type}) - ${self.price_per_night:.2f}/night"

class Guest:
    def __init__(self, name, contact_info):
        self.name = name
        self.contact_info = contact_info

    def __str__(self):
        return f"Guest: {self.name}, Contact: {self.contact_info}"

class Reservation:
    def __init__(self, reservation_id, guest, room, check_in, check_out):
        self.reservation_id = reservation_id
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out

    def calculate_total_cost(self):
        nights = (self.check_out - self.check_in).days
        return nights * self.room.price_per_night

    def __str__(self):
        return (f"Reservation ID: {self.reservation_id}\n"
                f"Guest: {self.guest.name}\n"
                f"Room: {self.room.room_number} ({self.room.room_type})\n"
                f"Check-in: {self.check_in}, Check-out: {self.check_out}\n"
                f"Total Cost: ${self.calculate_total_cost():.2f}")

class Hotel:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.rooms = []
        self.reservations = []
        self.reservation_counter = 1

    def add_room(self, room):
        self.rooms.append(room)

    def auto_add_rooms(self, singles, doubles, suites):
        for i in range(1, singles + 1):
            self.add_room(Room(100 + i, "Single", 100))
        for i in range(1, doubles + 1):
            self.add_room(Room(200 + i, "Double", 150))
        for i in range(1, suites + 1):
            self.add_room(Room(300 + i, "Suite", 300))

    def is_room_available(self, room, check_in, check_out):
        for r in self.reservations:
            if r.room.room_number == room.room_number:
                if not (check_out <= r.check_in or check_in >= r.check_out):
                    return False
        return True

    def find_available_room(self, room_type, check_in, check_out):
        for r in self.rooms:
            if r.room_type.lower() == room_type.lower() and self.is_room_available(r, check_in, check_out):
                return r
        return None

    def make_reservation(self, guest, room_type, check_in, nights):
        check_out = check_in + datetime.timedelta(days=nights)
        room = self.find_available_room(room_type, check_in, check_out)
        if room:
            reservation_id = f"RES-{self.reservation_counter:03d}"
            self.reservation_counter += 1
            reservation = Reservation(reservation_id, guest, room, check_in, check_out)
            self.reservations.append(reservation)
            self.save_reservations_to_file()
            return reservation
        return None

    def cancel_reservation(self, reservation_id):
        for i, r in enumerate(self.reservations):
            if r.reservation_id == reservation_id:
                del self.reservations[i]
                self.save_reservations_to_file()
                print(f"Reservation {reservation_id} canceled.")
                return
        print("Reservation ID not found.")

    def list_available_rooms(self, check_in, nights, room_type):
        check_out = check_in + datetime.timedelta(days=nights)
        found = False
        for r in self.rooms:
            if r.room_type.lower() == room_type.lower() and self.is_room_available(r, check_in, check_out):
                print(r)
                found = True
        if not found:
            print("No available rooms for the given date.")

    def list_reservations(self):
        if not self.reservations:
            print("No current reservations.")
        else:
            for r in self.reservations:
                print(r)
                print("-" * 40)

    def save_reservations_to_file(self):
        with open("reservations.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Reservation ID", "Guest Name", "Room Number", "Room Type", "Check-in Date", "Check-out Date", "Total Cost"])
            for r in self.reservations:
                writer.writerow([
                    r.reservation_id, r.guest.name, r.room.room_number, r.room.room_type,
                    r.check_in, r.check_out, f"{r.calculate_total_cost():.2f}"
                ])

    def load_reservations_from_file(self):
        if not os.path.exists("reservations.csv"):
            return
        with open("reservations.csv", "r", newline='') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for parts in reader:
                if len(parts) < 7:
                    continue
                guest = Guest(parts[1], "N/A")
                room = self.find_available_room(parts[3], datetime.date.fromisoformat(parts[4]), datetime.date.fromisoformat(parts[5]))
                if room:
                    self.reservations.append(Reservation(
                        parts[0], guest, room,
                        datetime.date.fromisoformat(parts[4]),
                        datetime.date.fromisoformat(parts[5])
                    ))

def main():
    hotel = Hotel("Modern Hotel", "123 Main Street")
    hotel.auto_add_rooms(10, 10, 10)
    hotel.load_reservations_from_file()

    while True:
        print("\nWelcome to Modern Hotel Reservation System")
        print("1. Make a Reservation")
        print("2. View Current Reservations")
        print("3. Cancel a Reservation")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            name = input("Enter guest name: ")
            contact = input("Enter guest contact info: ")
            guest = Guest(name, contact)

            # Room type input with validation
            room_type = None
            while room_type is None:
                t = input("Enter room type (Single/Double/Suite): ").strip()
                if t.lower() in ["single", "double", "suite"]:
                    room_type = t
                else:
                    print("Invalid room type. Please enter Single, Double, or Suite.")

            # Check-in date input with validation
            check_in = None
            while check_in is None:
                print("Select Check-in Date:")
                today = datetime.date.today()
                print(f"1. Today ({today})")
                print(f"2. Tomorrow ({today + datetime.timedelta(days=1)})")
                print("3. Enter custom date")
                date_choice = input("Choice: ").strip()
                if date_choice == "1":
                    check_in = today
                elif date_choice == "2":
                    check_in = today + datetime.timedelta(days=1)
                elif date_choice == "3":
                    while True:
                        date_str = input("Enter check-in date (YYYY-MM-DD): ")
                        try:
                            check_in = datetime.date.fromisoformat(date_str)
                            break
                        except Exception:
                            print("Invalid format. Please enter in YYYY-MM-DD.")
                else:
                    print("Invalid choice. Try again.")

            # Nights input with validation
            while True:
                try:
                    nights = int(input("How many nights will the guest stay? "))
                    if nights > 0:
                        break
                    else:
                        print("Please enter a positive number.")
                except Exception:
                    print("Invalid number. Please enter a valid integer.")

            hotel.list_available_rooms(check_in, nights, room_type)
            res = hotel.make_reservation(guest, room_type, check_in, nights)
            if res:
                print("Reservation successful!")
                print(res)
            else:
                print("No available room for that period.")

        elif choice == "2":
            hotel.list_reservations()
        elif choice == "3":
            reservation_id = input("Enter reservation ID to cancel: ")
            hotel.cancel_reservation(reservation_id)
        elif choice == "4":
            print("Thank you for using the system. Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
