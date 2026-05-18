"""
╔══════════════════════════════════════════════════════════╗
║         AIRLINE MANAGEMENT SYSTEM — Python OOP           ║
║         Clean • Modular • Beginner-Friendly              ║
╚══════════════════════════════════════════════════════════╝
"""

import uuid
import json
import os
from datetime import datetime


# ──────────────────────────────────────────────
# BASE CLASS: Person (Inheritance demonstration)
# ──────────────────────────────────────────────
class Person:
    """Base class for any person in the system."""

    def __init__(self, name: str, passport_number: str):
        self._name = name
        self._passport_number = passport_number

    @property
    def name(self) -> str:
        return self._name

    @property
    def passport_number(self) -> str:
        return self._passport_number

    def __str__(self) -> str:
        return f"{self._name} (Passport: {self._passport_number})"


# ──────────────────────────────────────────────
# CLASS: SeatClass  (Economy / Business)
# ──────────────────────────────────────────────
class SeatClass:
    ECONOMY = "Economy"
    BUSINESS = "Business"

    # Pricing per seat class
    PRICES = {
        ECONOMY: 150.0,
        BUSINESS: 450.0,
    }

    @staticmethod
    def get_price(seat_class: str) -> float:
        return SeatClass.PRICES.get(seat_class, 150.0)


# ──────────────────────────────────────────────
# CLASS: Flight
# ──────────────────────────────────────────────
class Flight:
    """Represents a single airline flight."""

    def __init__(
        self,
        flight_id: str,
        source: str,
        destination: str,
        departure_time: str,
        total_economy_seats: int = 20,
        total_business_seats: int = 5,
    ):
        self.__flight_id = flight_id
        self.__source = source.strip().title()
        self.__destination = destination.strip().title()
        self.__departure_time = departure_time

        # Build seat map: seat_id -> {"class": ..., "occupied": bool}
        self.__seat_map: dict[str, dict] = {}
        self.__total_seats = total_economy_seats + total_business_seats

        # Economy seats: E1, E2, ...
        for i in range(1, total_economy_seats + 1):
            seat_id = f"E{i}"
            self.__seat_map[seat_id] = {"class": SeatClass.ECONOMY, "occupied": False}

        # Business seats: B1, B2, ...
        for i in range(1, total_business_seats + 1):
            seat_id = f"B{i}"
            self.__seat_map[seat_id] = {"class": SeatClass.BUSINESS, "occupied": False}

    # ── Properties (read-only access) ──
    @property
    def flight_id(self) -> str:
        return self.__flight_id

    @property
    def source(self) -> str:
        return self.__source

    @property
    def destination(self) -> str:
        return self.__destination

    @property
    def departure_time(self) -> str:
        return self.__departure_time

    @property
    def total_seats(self) -> int:
        return self.__total_seats

    @property
    def available_seats(self) -> int:
        return sum(1 for s in self.__seat_map.values() if not s["occupied"])

    @property
    def seat_map(self) -> dict:
        return dict(self.__seat_map)  # return a copy

    # ── Methods ──
    def check_availability(self, seat_class: str = None) -> bool:
        """Return True if at least one seat is available (optionally filtered by class)."""
        for seat_info in self.__seat_map.values():
            if seat_info["occupied"]:
                continue
            if seat_class is None or seat_info["class"] == seat_class:
                return True
        return False

    def assign_seat(self, seat_class: str = SeatClass.ECONOMY) -> str | None:
        """Assign the first available seat of given class. Returns seat_id or None."""
        for seat_id, seat_info in self.__seat_map.items():
            if not seat_info["occupied"] and seat_info["class"] == seat_class:
                self.__seat_map[seat_id]["occupied"] = True
                return seat_id
        return None

    def cancel_seat(self, seat_id: str) -> bool:
        """Free a seat by its ID. Returns True on success."""
        if seat_id in self.__seat_map and self.__seat_map[seat_id]["occupied"]:
            self.__seat_map[seat_id]["occupied"] = False
            return True
        return False

    def display(self):
        """Print a formatted flight summary."""
        eco_total = sum(1 for s in self.__seat_map.values() if s["class"] == SeatClass.ECONOMY)
        bus_total = sum(1 for s in self.__seat_map.values() if s["class"] == SeatClass.BUSINESS)
        eco_avail = sum(
            1 for s in self.__seat_map.values()
            if s["class"] == SeatClass.ECONOMY and not s["occupied"]
        )
        bus_avail = sum(
            1 for s in self.__seat_map.values()
            if s["class"] == SeatClass.BUSINESS and not s["occupied"]
        )

        print(f"""
  ┌─────────────────────────────────────────────┐
  │  Flight ID   : {self.__flight_id:<28} │
  │  Route       : {self.__source} → {self.__destination:<20} │
  │  Departure   : {self.__departure_time:<28} │
  │  Economy     : {eco_avail}/{eco_total} available  (${SeatClass.PRICES[SeatClass.ECONOMY]:.0f}/seat)  │
  │  Business    : {bus_avail}/{bus_total} available  (${SeatClass.PRICES[SeatClass.BUSINESS]:.0f}/seat)  │
  └─────────────────────────────────────────────┘""")

    def to_dict(self) -> dict:
        """Serialize flight to dict for JSON storage."""
        return {
            "flight_id": self.__flight_id,
            "source": self.__source,
            "destination": self.__destination,
            "departure_time": self.__departure_time,
            "seat_map": self.__seat_map,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Flight":
        """Reconstruct a Flight from a saved dict."""
        # Count seats from seat_map
        eco = sum(1 for s in data["seat_map"].values() if s["class"] == SeatClass.ECONOMY)
        bus = sum(1 for s in data["seat_map"].values() if s["class"] == SeatClass.BUSINESS)
        flight = cls(
            data["flight_id"],
            data["source"],
            data["destination"],
            data["departure_time"],
            eco,
            bus,
        )
        # Restore seat occupancy
        flight._Flight__seat_map = data["seat_map"]
        return flight


# ──────────────────────────────────────────────
# CLASS: Passenger  (extends Person)
# ──────────────────────────────────────────────
class Passenger(Person):
    """A registered airline passenger."""

    def __init__(self, passenger_id: str, name: str, passport_number: str):
        super().__init__(name, passport_number)
        self.__passenger_id = passenger_id
        self.__ticket_ids: list[str] = []   # list of ticket IDs

    @property
    def passenger_id(self) -> str:
        return self.__passenger_id

    @property
    def ticket_ids(self) -> list[str]:
        return list(self.__ticket_ids)

    def add_ticket(self, ticket_id: str):
        self.__ticket_ids.append(ticket_id)

    def remove_ticket(self, ticket_id: str):
        if ticket_id in self.__ticket_ids:
            self.__ticket_ids.remove(ticket_id)

    def view_bookings(self, tickets_dict: dict):
        """Print all bookings for this passenger."""
        my_tickets = [t for t in tickets_dict.values() if t.ticket_id in self.__ticket_ids]
        if not my_tickets:
            print("  No bookings found.")
            return
        for ticket in my_tickets:
            ticket.display()

    def to_dict(self) -> dict:
        return {
            "passenger_id": self.__passenger_id,
            "name": self._name,
            "passport_number": self._passport_number,
            "ticket_ids": self.__ticket_ids,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Passenger":
        p = cls(data["passenger_id"], data["name"], data["passport_number"])
        p._Passenger__ticket_ids = data.get("ticket_ids", [])
        return p


# ──────────────────────────────────────────────
# CLASS: Ticket
# ──────────────────────────────────────────────
class Ticket:
    """Represents a booking between a Passenger and a Flight."""

    STATUS_BOOKED = "Booked"
    STATUS_CANCELLED = "Cancelled"

    def __init__(
        self,
        passenger: Passenger,
        flight: Flight,
        seat_number: str,
        seat_class: str,
        ticket_id: str = None,
    ):
        # Auto-generate ticket ID if not provided (e.g., when loading from JSON)
        self.__ticket_id = ticket_id or f"TKT-{str(uuid.uuid4())[:8].upper()}"
        self.__passenger = passenger
        self.__flight = flight
        self.__seat_number = seat_number
        self.__seat_class = seat_class
        self.__status = Ticket.STATUS_BOOKED
        self.__price = SeatClass.get_price(seat_class)
        self.__booked_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Properties ──
    @property
    def ticket_id(self) -> str:
        return self.__ticket_id

    @property
    def passenger(self) -> Passenger:
        return self.__passenger

    @property
    def flight(self) -> Flight:
        return self.__flight

    @property
    def seat_number(self) -> str:
        return self.__seat_number

    @property
    def status(self) -> str:
        return self.__status

    # ── Methods ──
    def cancel_ticket(self) -> bool:
        """Cancel this ticket and free the seat on the flight."""
        if self.__status == Ticket.STATUS_CANCELLED:
            return False
        success = self.__flight.cancel_seat(self.__seat_number)
        if success:
            self.__status = Ticket.STATUS_CANCELLED
            self.__passenger.remove_ticket(self.__ticket_id)
        return success

    def display(self):
        status_icon = "✓" if self.__status == Ticket.STATUS_BOOKED else "✗"
        print(f"""
  ┌─────────────────────────────────────────────┐
  │  Ticket ID   : {self.__ticket_id:<28} │
  │  Status      : {status_icon} {self.__status:<26} │
  │  Passenger   : {self.__passenger.name:<28} │
  │  Flight      : {self.__flight.flight_id:<28} │
  │  Route       : {self.__flight.source} → {self.__flight.destination:<20} │
  │  Departure   : {self.__flight.departure_time:<28} │
  │  Seat        : {self.__seat_number} ({self.__seat_class}){'':<20} │
  │  Price       : ${self.__price:<27.2f} │
  │  Booked At   : {self.__booked_at:<28} │
  └─────────────────────────────────────────────┘""")

    def to_dict(self) -> dict:
        return {
            "ticket_id": self.__ticket_id,
            "passenger_id": self.__passenger.passenger_id,
            "flight_id": self.__flight.flight_id,
            "seat_number": self.__seat_number,
            "seat_class": self.__seat_class,
            "status": self.__status,
            "price": self.__price,
            "booked_at": self.__booked_at,
        }


# ──────────────────────────────────────────────
# CLASS: AirlineSystem  (Main Controller)
# ──────────────────────────────────────────────
class AirlineSystem:
    """Central controller that manages flights, passengers, and tickets."""

    DATA_FILE = "airline_data.json"

    def __init__(self):
        self.__flights: dict[str, Flight] = {}
        self.__passengers: dict[str, Passenger] = {}
        self.__tickets: dict[str, Ticket] = {}
        self.__load_data()

    # ══════════════════════════════════════════
    # FLIGHT MANAGEMENT
    # ══════════════════════════════════════════

    def add_flight(self):
        """Prompt user and add a new flight."""
        print("\n  ── Add New Flight ──")
        try:
            flight_id = input("  Flight ID (e.g. PK301): ").strip().upper()
            if not flight_id:
                print("  ✗ Flight ID cannot be empty.")
                return
            if flight_id in self.__flights:
                print("  ✗ A flight with this ID already exists.")
                return

            source = input("  Source city: ").strip()
            destination = input("  Destination city: ").strip()
            departure_time = input("  Departure time (e.g. 2025-08-15 14:30): ").strip()
            economy_seats = int(input("  Number of Economy seats (default 20): ") or 20)
            business_seats = int(input("  Number of Business seats (default 5): ") or 5)

            if economy_seats < 0 or business_seats < 0:
                print("  ✗ Seat count cannot be negative.")
                return

            flight = Flight(flight_id, source, destination, departure_time, economy_seats, business_seats)
            self.__flights[flight_id] = flight
            self.__save_data()
            print(f"\n  ✓ Flight {flight_id} added successfully!")

        except ValueError:
            print("  ✗ Invalid input. Please enter valid numbers for seats.")

    def view_flights(self):
        """Display all registered flights."""
        if not self.__flights:
            print("\n  No flights registered yet.")
            return
        print(f"\n  ── All Flights ({len(self.__flights)} total) ──")
        for flight in self.__flights.values():
            flight.display()

    def search_flight(self):
        """Search flights by source and destination."""
        print("\n  ── Search Flights ──")
        source = input("  From (city): ").strip().title()
        destination = input("  To (city): ").strip().title()

        results = [
            f for f in self.__flights.values()
            if f.source == source and f.destination == destination
        ]

        if not results:
            print(f"\n  No flights found from {source} to {destination}.")
            return

        print(f"\n  Found {len(results)} flight(s) from {source} to {destination}:")
        for flight in results:
            flight.display()

    # ══════════════════════════════════════════
    # PASSENGER MANAGEMENT
    # ══════════════════════════════════════════

    def register_passenger(self):
        """Register a new passenger."""
        print("\n  ── Register Passenger ──")
        name = input("  Full name: ").strip()
        if not name:
            print("  ✗ Name cannot be empty.")
            return

        passport = input("  Passport number: ").strip().upper()
        if not passport:
            print("  ✗ Passport number cannot be empty.")
            return

        # Check for duplicate passport
        for p in self.__passengers.values():
            if p.passport_number == passport:
                print("  ✗ A passenger with this passport number already exists.")
                return

        passenger_id = f"PAX-{str(uuid.uuid4())[:6].upper()}"
        passenger = Passenger(passenger_id, name, passport)
        self.__passengers[passenger_id] = passenger
        self.__save_data()
        print(f"\n  ✓ Passenger registered! Your Passenger ID: {passenger_id}")

    # ══════════════════════════════════════════
    # TICKET BOOKING
    # ══════════════════════════════════════════

    def book_ticket(self):
        """Book a ticket for a passenger on a flight."""
        print("\n  ── Book Ticket ──")

        # Get passenger
        passenger_id = input("  Enter your Passenger ID: ").strip().upper()
        passenger = self.__passengers.get(passenger_id)
        if not passenger:
            print("  ✗ Passenger not found. Please register first.")
            return

        # Get flight
        flight_id = input("  Enter Flight ID: ").strip().upper()
        flight = self.__flights.get(flight_id)
        if not flight:
            print("  ✗ Flight not found.")
            return

        # Choose seat class
        print("\n  Seat Class:")
        print(f"    [1] Economy   — ${SeatClass.PRICES[SeatClass.ECONOMY]:.0f}")
        print(f"    [2] Business  — ${SeatClass.PRICES[SeatClass.BUSINESS]:.0f}")

        try:
            choice = int(input("  Choose (1/2): "))
            seat_class = SeatClass.ECONOMY if choice == 1 else SeatClass.BUSINESS
        except ValueError:
            print("  ✗ Invalid choice.")
            return

        # Check availability
        if not flight.check_availability(seat_class):
            print(f"  ✗ No {seat_class} seats available on this flight.")
            return

        # Assign seat
        seat_number = flight.assign_seat(seat_class)
        if not seat_number:
            print("  ✗ Could not assign a seat. Please try again.")
            return

        # Create ticket
        ticket = Ticket(passenger, flight, seat_number, seat_class)
        self.__tickets[ticket.ticket_id] = ticket
        passenger.add_ticket(ticket.ticket_id)
        self.__save_data()

        print(f"\n  ✓ Ticket booked successfully!")
        ticket.display()

    # ══════════════════════════════════════════
    # TICKET CANCELLATION
    # ══════════════════════════════════════════

    def cancel_ticket(self):
        """Cancel a ticket by ticket ID."""
        print("\n  ── Cancel Ticket ──")
        ticket_id = input("  Enter Ticket ID: ").strip().upper()

        ticket = self.__tickets.get(ticket_id)
        if not ticket:
            print("  ✗ Ticket not found.")
            return

        if ticket.status == Ticket.STATUS_CANCELLED:
            print("  ✗ This ticket is already cancelled.")
            return

        confirm = input(f"  Cancel ticket {ticket_id} for {ticket.passenger.name}? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("  Cancellation aborted.")
            return

        success = ticket.cancel_ticket()
        if success:
            self.__save_data()
            print(f"\n  ✓ Ticket {ticket_id} has been cancelled.")
        else:
            print("  ✗ Failed to cancel the ticket.")

    # ══════════════════════════════════════════
    # BOOKING HISTORY
    # ══════════════════════════════════════════

    def view_passenger_bookings(self):
        """Show all bookings for a given passenger."""
        print("\n  ── Passenger Bookings ──")
        passenger_id = input("  Enter Passenger ID: ").strip().upper()

        passenger = self.__passengers.get(passenger_id)
        if not passenger:
            print("  ✗ Passenger not found.")
            return

        print(f"\n  Bookings for: {passenger.name}")
        passenger.view_bookings(self.__tickets)

    # ══════════════════════════════════════════
    # DATA PERSISTENCE  (JSON)
    # ══════════════════════════════════════════

    def __save_data(self):
        """Save all system data to a JSON file."""
        try:
            data = {
                "flights": {fid: f.to_dict() for fid, f in self.__flights.items()},
                "passengers": {pid: p.to_dict() for pid, p in self.__passengers.items()},
                "tickets": {tid: t.to_dict() for tid, t in self.__tickets.items()},
            }
            with open(self.DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"  ⚠ Warning: Could not save data — {e}")

    def __load_data(self):
        """Load system data from JSON file (if it exists)."""
        if not os.path.exists(self.DATA_FILE):
            return
        try:
            with open(self.DATA_FILE, "r") as f:
                data = json.load(f)

            # Restore flights
            for fid, fdata in data.get("flights", {}).items():
                self.__flights[fid] = Flight.from_dict(fdata)

            # Restore passengers
            for pid, pdata in data.get("passengers", {}).items():
                self.__passengers[pid] = Passenger.from_dict(pdata)

            # Restore tickets (need flight & passenger objects)
            for tid, tdata in data.get("tickets", {}).items():
                flight = self.__flights.get(tdata["flight_id"])
                passenger = self.__passengers.get(tdata["passenger_id"])
                if flight and passenger:
                    ticket = Ticket(
                        passenger,
                        flight,
                        tdata["seat_number"],
                        tdata["seat_class"],
                        ticket_id=tdata["ticket_id"],
                    )
                    # Restore status
                    ticket._Ticket__status = tdata["status"]
                    ticket._Ticket__price = tdata["price"]
                    ticket._Ticket__booked_at = tdata["booked_at"]
                    self.__tickets[tid] = ticket

            print(f"  ✓ Data loaded from {self.DATA_FILE}")

        except Exception as e:
            print(f"  ⚠ Warning: Could not load data — {e}")


# ──────────────────────────────────────────────
# CONSOLE MENU
# ──────────────────────────────────────────────

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║          ✈  AIRLINE MANAGEMENT SYSTEM  ✈                ║
║              Powered by Python OOP                       ║
╚══════════════════════════════════════════════════════════╝""")


def print_menu():
    print("""
  ┌───────────────────────────────────┐
  │           MAIN MENU               │
  ├───────────────────────────────────┤
  │  [1]  Add Flight                  │
  │  [2]  View All Flights            │
  │  [3]  Search Flight               │
  │  [4]  Register Passenger          │
  │  [5]  Book Ticket                 │
  │  [6]  Cancel Ticket               │
  │  [7]  View Passenger Bookings     │
  │  [8]  Exit                        │
  └───────────────────────────────────┘""")


def main():
    print_banner()
    system = AirlineSystem()

    while True:
        print_menu()
        try:
            choice = input("\n  Enter your choice (1-8): ").strip()

            if choice == "1":
                system.add_flight()
            elif choice == "2":
                system.view_flights()
            elif choice == "3":
                system.search_flight()
            elif choice == "4":
                system.register_passenger()
            elif choice == "5":
                system.book_ticket()
            elif choice == "6":
                system.cancel_ticket()
            elif choice == "7":
                system.view_passenger_bookings()
            elif choice == "8":
                print("\n  ✈ Thank you for using Airline Management System. Goodbye!\n")
                break
            else:
                print("  ✗ Invalid choice. Please enter a number between 1 and 8.")

        except KeyboardInterrupt:
            print("\n\n  ✈ Exiting. Safe travels!\n")
            break


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    main()