import java.io.*;
import java.time.LocalDate;
import java.util.*;

class Room {
    private int roomNumber;
    private String roomType;
    private double pricePerNight;

    public Room(int roomNumber, String roomType, double pricePerNight) {
        this.roomNumber = roomNumber;
        this.roomType = roomType;
        this.pricePerNight = pricePerNight;
    }

    public int getRoomNumber() {
        return roomNumber;
    }

    public String getRoomType() {
        return roomType;
    }

    public double getPricePerNight() {
        return pricePerNight;
    }

    @Override
    public String toString() {
        return "Room " + roomNumber + " (" + roomType + ") - $" + pricePerNight + "/night";
    }
}

class Guest {
    private String name;
    private String contactInfo;

    public Guest(String name, String contactInfo) {
        this.name = name;
        this.contactInfo = contactInfo;
    }

    public String getName() {
        return name;
    }

    public String getContactInfo() {
        return contactInfo;
    }

    @Override
    public String toString() {
        return "Guest: " + name + ", Contact: " + contactInfo;
    }
}

class Reservation {
    private String reservationId;
    private Guest guest;
    private Room room;
    private LocalDate checkInDate;
    private LocalDate checkOutDate;

    public Reservation(String reservationId, Guest guest, Room room, LocalDate checkInDate, LocalDate checkOutDate) {
        this.reservationId = reservationId;
        this.guest = guest;
        this.room = room;
        this.checkInDate = checkInDate;
        this.checkOutDate = checkOutDate;
    }

    public String getReservationId() {
        return reservationId;
    }

    public Guest getGuest() {
        return guest;
    }

    public Room getRoom() {
        return room;
    }

    public LocalDate getCheckInDate() {
        return checkInDate;
    }

    public LocalDate getCheckOutDate() {
        return checkOutDate;
    }

    public double calculateTotalCost() {
        long nights = java.time.temporal.ChronoUnit.DAYS.between(checkInDate, checkOutDate);
        return nights * room.getPricePerNight();
    }

    @Override
    public String toString() {
        return "Reservation ID: " + reservationId + "\n"
                + "Guest: " + guest.getName() + "\n"
                + "Room: " + room.getRoomNumber() + " (" + room.getRoomType() + ")\n"
                + "Check-in: " + checkInDate + ", Check-out: " + checkOutDate + "\n"
                + "Total Cost: $" + calculateTotalCost();
    }
}

class Hotel {
    private String name;
    private String address;
    private List<Room> rooms = new ArrayList<>();
    private List<Reservation> reservations = new ArrayList<>();
    private int reservationCounter = 1;

    public Hotel(String name, String address) {
        this.name = name;
        this.address = address;
    }

    public void addRoom(Room room) {
        rooms.add(room);
    }

    public void autoAddRooms(int singles, int doubles, int suites) {
        for (int i = 1; i <= singles; i++)
            addRoom(new Room(100 + i, "Single", 100));
        for (int i = 1; i <= doubles; i++)
            addRoom(new Room(200 + i, "Double", 150));
        for (int i = 1; i <= suites; i++)
            addRoom(new Room(300 + i, "Suite", 300));
    }

    public boolean isRoomAvailable(Room room, LocalDate checkIn, LocalDate checkOut) {
        for (Reservation r : reservations) {
            if (r.getRoom().getRoomNumber() == room.getRoomNumber()) {
                if (!(checkOut.isBefore(r.getCheckInDate()) || checkIn.isAfter(r.getCheckOutDate()))) {
                    return false;
                }
            }
        }
        return true;
    }

    public Room findAvailableRoom(String type, LocalDate checkIn, LocalDate checkOut) {
        for (Room r : rooms) {
            if (r.getRoomType().equalsIgnoreCase(type) && isRoomAvailable(r, checkIn, checkOut)) {
                return r;
            }
        }
        return null;
    }

    public Reservation makeReservation(Guest guest, String type, LocalDate checkIn, int nights) {
        LocalDate checkOut = checkIn.plusDays(nights);
        Room room = findAvailableRoom(type, checkIn, checkOut);
        if (room != null) {
            Reservation reservation = new Reservation("RES-" + (reservationCounter++), guest, room, checkIn, checkOut);
            reservations.add(reservation);
            saveReservationsToFile();
            return reservation;
        }
        return null;
    }

    public void cancelReservation(String reservationId) {
        Iterator<Reservation> it = reservations.iterator();
        while (it.hasNext()) {
            Reservation r = it.next();
            if (r.getReservationId().equals(reservationId)) {
                it.remove();
                saveReservationsToFile();
                System.out.println("Reservation " + reservationId + " canceled.");
                return;
            }
        }
        System.out.println("Reservation ID not found.");
    }

    public void listAvailableRooms(LocalDate checkIn, int nights, String type) {
        LocalDate checkOut = checkIn.plusDays(nights);
        boolean found = false;
        for (Room r : rooms) {
            if (r.getRoomType().equalsIgnoreCase(type) && isRoomAvailable(r, checkIn, checkOut)) {
                System.out.println(r);
                found = true;
            }
        }
        if (!found)
            System.out.println("No available rooms for the given date.");
    }

    public void listReservations() {
        if (reservations.isEmpty())
            System.out.println("No current reservations.");
        else
            for (Reservation r : reservations) {
                System.out.println(r);
                System.out.println("----------------------------------------");
            }
    }

    public void saveReservationsToFile() {
        try (PrintWriter writer = new PrintWriter(new File("reservations.csv"))) {
            writer.println("Reservation ID,Guest Name,Room Number,Room Type,Check-in Date,Check-out Date,Total Cost");
            for (Reservation r : reservations) {
                writer.println(r.getReservationId() + "," + r.getGuest().getName() + "," +
                        r.getRoom().getRoomNumber() + "," + r.getRoom().getRoomType() + "," +
                        r.getCheckInDate() + "," + r.getCheckOutDate() + "," + r.calculateTotalCost());
            }
        } catch (IOException e) {
            System.out.println("Error saving reservations: " + e.getMessage());
        }
    }

    public void loadReservationsFromFile() {
        try (BufferedReader reader = new BufferedReader(new FileReader("reservations.csv"))) {
            String line = reader.readLine();
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length < 7)
                    continue;
                Guest guest = new Guest(parts[1], "N/A");
                Room room = findAvailableRoom(parts[3], LocalDate.parse(parts[4]), LocalDate.parse(parts[5]));
                if (room != null) {
                    reservations.add(new Reservation(parts[0], guest, room, LocalDate.parse(parts[4]),
                            LocalDate.parse(parts[5])));
                }
            }
        } catch (IOException e) {
            System.out.println("Error loading reservations: " + e.getMessage());
        }
    }
}

public class ModernHotelSYS {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Hotel hotel = new Hotel("Modern Hotel", "123 Main Street");
        hotel.autoAddRooms(10, 10, 10);
        hotel.loadReservationsFromFile();

        while (true) {
            System.out.println("\nWelcome to Modern Hotel Reservation System");
            System.out.println("1. Make a Reservation");
            System.out.println("2. View Current Reservations");
            System.out.println("3. Cancel a Reservation");
            System.out.println("4. Exit");
            System.out.print("Enter your choice: ");
            String choice = scanner.nextLine();

            switch (choice) {
                case "1":
                    System.out.print("Enter guest name: ");
                    String name = scanner.nextLine();
                    System.out.print("Enter guest contact info: ");
                    String contact = scanner.nextLine();
                    Guest guest = new Guest(name, contact);

                    System.out.print("Enter room type (Single/Double/Suite): ");
                    String type = scanner.nextLine();

                    LocalDate checkIn = null;
                    while (checkIn == null) {
                        System.out.println("Select Check-in Date:");
                        System.out.println("1. Today (" + LocalDate.now() + ")");
                        System.out.println("2. Tomorrow (" + LocalDate.now().plusDays(1) + ")");
                        System.out.println("3. Enter custom date");
                        System.out.print("Choice: ");
                        String dateChoice = scanner.nextLine();

                        switch (dateChoice) {
                            case "1":
                                checkIn = LocalDate.now();
                                break;
                            case "2":
                                checkIn = LocalDate.now().plusDays(1);
                                break;
                            case "3":
                                System.out.print("Enter check-in date (YYYY-MM-DD): ");
                                try {
                                    checkIn = LocalDate.parse(scanner.nextLine());
                                } catch (Exception e) {
                                    System.out.println("Invalid format. Try again.");
                                }
                                break;
                            default:
                                System.out.println("Invalid choice. Try again.");
                        }
                    }

                    System.out.print("How many nights will the guest stay? ");
                    int nights = Integer.parseInt(scanner.nextLine());

                    hotel.listAvailableRooms(checkIn, nights, type);
                    Reservation res = hotel.makeReservation(guest, type, checkIn, nights);
                    if (res != null) {
                        System.out.println("Reservation successful!");
                        System.out.println(res);
                    } else {
                        System.out.println("No available room for that period.");
                    }
                    break;
                case "2":
                    hotel.listReservations();
                    break;
                case "3":
                    System.out.print("Enter reservation ID to cancel: ");
                    hotel.cancelReservation(scanner.nextLine());
                    break;
                case "4":
                    System.out.println("Thank you for using the system. Goodbye!");
                    return;
                default:
                    System.out.println("Invalid option.");
            }
        }
    }
}
