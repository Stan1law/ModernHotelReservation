import sqlite3
import datetime


reservation_counter = 1


def get_next_reservation_id():
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT reservation_id FROM reservations ORDER BY reservation_id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        try:
            last_number = int(row[0].split("-")[1])
            return last_number + 1
        except:
            return 1
    return 1


def init_db():
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    # create tables if they don't exist
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS rooms (
        room_number INTEGER PRIMARY KEY,
        room_type TEXT,
        price_per_night REAL,
        is_available INTEGER DEFAULT 1
    )"""
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS guests (
        guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT
    )"""
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS reservations (
        reservation_id TEXT PRIMARY KEY,
        guest_id INTEGER,
        room_number INTEGER,
        check_in_date TEXT,
        check_out_date TEXT,
        total_cost REAL,
        FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
        FOREIGN KEY (room_number) REFERENCES rooms(room_number)
    )"""
    )


def add_room(room_number, room_type, price_per_night):
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO rooms (room_number, room_type, price_per_night) VALUES (?, ?, ?)",
        (room_number, room_type, price_per_night),
    )

    conn.commit()
    conn.close()

    print(f"Room {room_number} added to database.")


def auto_add_rooms():
    for i in range(1, 11):
        add_room(100 + i, "Single", 100)
        add_room(200 + i, "Double", 150)
        add_room(300 + i, "Suite", 300)


def list_available_rooms():
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT room_number, room_type, price_per_night FROM rooms WHERE is_available = 1"
    )
    rows = cursor.fetchall()

    if rows:
        print("\nAvailable Rooms:")
        for room_number, room_type, price in rows:
            print(f"Room: {room_number} ({room_type}) - ${price}/night")
    else:
        print("No rooms available.")

    conn.close()


def make_reservation():
    global reservation_counter
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    # get guest details
    name = input("Enter guest name: ")
    contact = input("Enter guest contact info: ")

    # Insert guest into 'guests' table
    cursor.execute("INSERT INTO guests (name, contact) VALUES (?, ?)", (name, contact))
    guest_id = cursor.lastrowid  # gets the auto incremented guest_id

    # choose room type
    room_type = input("Enter room type (Single/Double/Suite): ").capitalize()

    # Find an available room
    cursor.execute(
        "SELECT room_number, price_per_night FROM rooms WHERE room_type = ? AND is_available = 1",
        (room_type,),
    )
    room = cursor.fetchone()

    if not room:
        print("No available rooms for that type")
        conn.close()
        return

    room_number, price = room
    print(f"Room {room_number} selected at ${price}/night")

    # choose check-in date
    print("Select Check-in Date")
    print(f"1. Today ({datetime.date.today()})")
    print(f"2. Tomorrow ({datetime.date.today() + datetime.timedelta(days=1)})")
    print("3. Enter custom date")

    while True:
        choice = input("Choice: ")
        if choice == "1":
            check_in = datetime.date.today()
            break
        elif choice == "2":
            check_in = datetime.date.today() + datetime.timedelta(days=1)
            break
        elif choice == "3":
            try:
                user_input = input("Enter check-in date (YYYY-MM-DD): ")
                check_in = datetime.datetime.strptime(user_input, "%Y-%m-%d").date()
                break
            except:
                print("Invalid date format.")

        else:
            print("Invalid options.")

    # stay duration
    nights = int(input("How many nights will the guest stay? "))
    check_out = check_in + datetime.timedelta(days=nights)
    total_cost = nights * price

    # create reservation
    reservation_id = f"RES-{reservation_counter:03d}"
    reservation_counter += 1

    cursor.execute(
        "INSERT INTO reservations (reservation_id, guest_id, room_number, check_in_date, check_out_date, total_cost) VALUES (?, ?, ?, ?, ?, ?)",
        (
            reservation_id,
            guest_id,
            room_number,
            check_in.isoformat(),
            check_out.isoformat(),
            total_cost,
        ),
    )

    # update room to not available
    cursor.execute(
        "UPDATE rooms SET is_available = 0 WHERE room_number = ?", (room_number,)
    )

    conn.commit()
    conn.close()

    print("Reservation Successful!")
    print(f"Reservation ID: {reservation_id}")
    print(f"Check-in: {check_in}")
    print(f"Check-out: {check_out}")
    print(f"Total cost: ${total_cost}")


def cancel_reservation():
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    reservation_id = input("Enter reservation ID to cancel: ")

    # Check if reservation exists
    cursor.execute(
        "SELECT room_number FROM reservations WHERE reservation_id = ?",
        (reservation_id,),
    )
    result = cursor.fetchone()

    if not result:
        print("Reservation not found.")
        conn.close()
        return

    room_number = result[0]

    # Delete reservation
    cursor.execute(
        "DELETE FROM reservations WHERE reservation_id = ?", (reservation_id,)
    )

    # Set room as available again
    cursor.execute(
        "UPDATE rooms SET is_available = 1 WHERE room_number = ?", (room_number,)
    )

    conn.commit()
    conn.close()

    print(
        f"Reservation {reservation_id} has been canceled and Room {room_number} is now available."
    )


def view_reservations():
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    query = """
    SELECT 
        r.reservation_id,
        g.name,
        g.contact,
        r.room_number,
        rooms.room_type,
        r.check_in_date,
        r.check_out_date,
        r.total_cost
    FROM reservations r
    JOIN guests g ON r.guest_id = g.guest_id
    JOIN rooms ON r.room_number = rooms.room_number
    ORDER BY r.check_in_date
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("No reservations found")
    else:
        print("\n=== Current Reservations ===")
        for row in rows:
            print(f"\nReservation ID: {row[0]}")
            print(f"Guest: {row[1]} (Contact: {row[2]})")
            print(f"Room: {row[3]} ({row[4]})")
            print(f"Check-in: {row[5]}")
            print(f"Check-out: {row[6]}")
            print(f"Total Cost: ${row[7]}")
            print("-" * 40)

    conn.close()


def search_reservation():
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    print("\nSearch By:")
    print("1. Guest name: ")
    print("2. Reservation ID: ")
    choice = input("Enter your choice: ")

    if choice == "1":
        keyword = input("Enter guest name keyword: ").strip()
        cursor.execute(
            """
            SELECT 
                r.reservation_id, g.name, g.contact, 
                r.room_number, rooms.room_type, 
                r.check_in_date, r.check_out_date, r.total_cost
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms ON r.room_number = rooms.room_number
            WHERE g.name LIKE ?
        """,
            ("%" + keyword + "%",),
        )

    elif choice == "2":
        res_id = input("Enter reservation ID: ").strip()
        cursor.execute(
            """
            SELECT 
                r.reservation_id, g.name, g.contact, 
                r.room_number, rooms.room_type, 
                r.check_in_date, r.check_out_date, r.total_cost
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms ON r.room_number = rooms.room_number
            WHERE r.reservation_id = ?
        """,
            (res_id,),
        )
    else:
        print("Invalid choice!")
        conn.close()
        return

    rows = cursor.fetchall()
    if not rows:
        print("No Matching reservations found.")
    else:
        for row in rows:
            print(f"\nReservation ID: {row[0]}")
            print(f"Guest: {row[1]} (Contact: {row[2]})")
            print(f"Room: {row[3]} ({row[4]})")
            print(f"Check-in: {row[5]}")
            print(f"Check-out: {row[6]}")
            print(f"Total Cost: ${row[7]}")
            print("-" * 40)

    conn.close()


def edit_reservation():
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()

    reservation_id = input("Enter reservation ID to edit").strip()

    # fetch the reservation details
    cursor.execute(
        """
        SELECT r.guest_id, g.name, g.contact, r.room_number, rooms.room_type,
               r.check_in_date, r.check_out_date
        FROM reservations r
        JOIN guests g ON r.guest_id = g.guest_id
        JOIN rooms ON r.room_number = rooms.room_number
        WHERE r.reservation_id = ?
    """,
        (reservation_id,),
    )
    result = cursor.fetchone()

    if not result:
        print("Reservation not found")
        conn.close()
        return

    (
        guest_id,
        current_name,
        current_contact,
        room_number,
        room_type,
        check_in,
        check_out,
    ) = result
    print("\n=== Current Reservation Info ===")
    print(f"Guest Name: {current_name}")
    print(f"Contact: {current_contact}")
    print(f"Room Type: {room_type}")
    print(f"Check-in: {check_in}")
    print(f"Check-out: {check_out}")

    # ask what to update
    new_name = (
        input("Enter new guest name (Leave a blank to keep current): ").strip()
        or current_name
    )
    new_contact = (
        input("Enter new contact (Leave a blank to keep current): ").strip()
        or current_contact
    )

    # ask for new room type
    new_room_type = (
        input("Enter new room type (Single/Double/Suite) or leave blank: ").strip()
        or room_type
    )
    cursor.execute(
        """
        SELECT room_number FROM rooms 
        WHERE room_type = ? AND is_available = 1
    """,
        (new_room_type,),
    )
    new_room = cursor.fetchone()
    if not new_room:
        print(f"No available {new_room_type} rooms. Keeping current room.")
        new_room_number = room_number
    else:
        # free up old room
        cursor.execute(
            "UPDATE rooms SET is_available = 1 WHERE room_number = ?", (room_number,)
        )
        new_room_number = new_room[0]
        cursor.execute(
            "UPDATE rooms SET is_available = 0 WHERE room_number = ?",
            (new_room_number,),
        )

    # check-in updates
    try:
        new_check_in = input(
            "Enter new check-in date (YYYY-MM-DD) or leave blank: "
        ).strip()
        new_check_in_date = (
            datetime.datetime.strptime(new_check_in, "%Y-%m%d").date()
            if new_check_in
            else datetime.datetime.strptime(check_in, "Y%-%m-%d").date()
        )
    except:
        print("Invalid date format: Keeping current date.")
        new_check_in_date = datetime.datetime.strptime(check_in, "%Y-%m-%d").date()

    try:
        nights = int(
            input("Enter number of nights (Leave blank to keep same length): ")
            or (datetime.datetime.strptime(check_in, "%Y-%m-%d").date()).days
        )
    except:
        nights = 1

    new_check_out_date = new_check_in_date + datetime.timedelta(days=nights)
    new_total_cost = nights * (
        150
        if new_room_type.lower() == "double"
        else 300 if new_room_type.lower() == "suite" else 100
    )

    # update database
    cursor.execute(
        "UPDATE guests SET name = ?, contact = ? WHERE guest_id = ?",
        (new_name, new_contact, guest_id),
    )
    cursor.execute(
        """
        UPDATE reservations
        SET room_number = ?, check_in_date = ?, check_out_date = ?, total_cost = ?
        WHERE reservation_id = ?
    """,
        (
            new_room_number,
            new_check_in_date,
            new_check_out_date,
            new_total_cost,
            reservation_id,
        ),
    )

    conn.commit()
    conn.close()
    print("\nReservation updated successfully!")


if __name__ == "__main__":
    init_db()

    reservation_counter = get_next_reservation_id()

    if input("Add rooms to database? (y/n): ").lower() == "y":
        auto_add_rooms()

    while True:
        print("\nHotel Reservation System (DB version)")
        print("1. List Available Rooms")
        print("2. Make Reservation")
        print("3. Cancel Reservation")
        print("4. View All Reservations")
        print("5. Search Reservation")
        print("6. Edit Reservation")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            list_available_rooms()
        elif choice == "2":
            make_reservation()
        elif choice == "3":
            cancel_reservation()
        elif choice == "4":
            view_reservations()
        elif choice == "5":
            search_reservation()
        elif choice == "6":
            edit_reservation()
        elif choice == "7":
            print("Thank you for using Modern Hotel Reservation!")
            break
        else:
            print("Invalid choice. Try again.")
