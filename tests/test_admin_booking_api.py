import unittest
from datetime import date, time, timedelta, datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.ride import Ride, RideStatus
from app.models.ride_request import RideRequest
from app.api.deps import get_current_admin


class TestAdminBookingAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls.admin_email = "test_booking_admin@example.com"
        cls.driver_email = "test_booking_driver@example.com"
        cls.passenger_email = "test_booking_passenger@example.com"

        # Admin
        existing_admin = cls.db.query(User).filter(User.email == cls.admin_email).first()
        if existing_admin:
            cls.admin = existing_admin
            cls.admin.role = "admin"
            cls.db.commit()
        else:
            cls.admin = User(
                full_name="Booking Super Admin",
                email=cls.admin_email,
                phone="9998800001",
                role="admin",
                email_verified=True,
            )
            cls.db.add(cls.admin)
            cls.db.commit()
            cls.db.refresh(cls.admin)

        # Driver
        existing_driver = cls.db.query(User).filter(User.email == cls.driver_email).first()
        if existing_driver:
            cls.driver = existing_driver
        else:
            cls.driver = User(
                full_name="Booking Test Driver",
                email=cls.driver_email,
                phone="9998800002",
                role="rider",
                email_verified=True,
            )
            cls.db.add(cls.driver)
            cls.db.commit()
            cls.db.refresh(cls.driver)

        # Passenger
        existing_pax = cls.db.query(User).filter(User.email == cls.passenger_email).first()
        if existing_pax:
            cls.passenger = existing_pax
        else:
            cls.passenger = User(
                full_name="Booking Test Passenger",
                email=cls.passenger_email,
                phone="9998800003",
                role="consumer",
                email_verified=True,
            )
            cls.db.add(cls.passenger)
            cls.db.commit()
            cls.db.refresh(cls.passenger)

        # Vehicle
        existing_veh = cls.db.query(Vehicle).filter(Vehicle.user_id == cls.driver.id).first()
        if existing_veh:
            cls.vehicle = existing_veh
        else:
            cls.vehicle = Vehicle(
                user_id=cls.driver.id,
                vehicle_type="Car",
                brand="Maruti",
                model="Swift",
                year=2022,
                color="Red",
                registration_number="KL-07-BK-1111",
                seating_capacity=4,
            )
            cls.db.add(cls.vehicle)
            cls.db.commit()
            cls.db.refresh(cls.vehicle)

        # Test Ride
        cls.test_ride = Ride(
            driver_id=cls.driver.id,
            vehicle_id=cls.vehicle.id,
            source="Maradu",
            destination="Edappally",
            route="Via NH66",
            travel_date=date.today() + timedelta(days=3),
            travel_time=time(10, 0),
            available_seats=2,
            status=RideStatus.UPCOMING.value,
        )
        cls.db.add(cls.test_ride)
        cls.db.commit()
        cls.db.refresh(cls.test_ride)

        # Test Accepted Booking (with 2 seats reserved)
        cls.test_booking = RideRequest(
            ride_id=cls.test_ride.ride_id,
            passenger_id=cls.passenger.id,
            seats_requested=2,
            status="accepted",
        )
        cls.db.add(cls.test_booking)
        cls.db.commit()
        cls.db.refresh(cls.test_booking)

        # Overrides
        app.dependency_overrides[get_current_admin] = lambda: cls.admin
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        try:
            cls.db.query(RideRequest).filter(RideRequest.ride_id == cls.test_ride.ride_id).delete()
            cls.db.query(Ride).filter(Ride.ride_id == cls.test_ride.ride_id).delete()
            cls.db.commit()
        except Exception:
            cls.db.rollback()
        cls.db.close()

    def test_01_get_admin_booking_statistics(self):
        res = self.client.get("/api/v1/admin/bookings/statistics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total", data)
        self.assertIn("pending", data)
        self.assertIn("accepted", data)
        self.assertIn("rejected", data)
        self.assertIn("cancelled", data)
        self.assertGreaterEqual(data["total"], 1)

    def test_02_get_admin_bookings_list(self):
        res = self.client.get("/api/v1/admin/bookings?page=1&size=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertIn("pages", data)
        self.assertTrue(any(item["booking_id"] == self.test_booking.ride_request_id for item in data["items"]))

        # Search test
        res_search = self.client.get("/api/v1/admin/bookings?search=Maradu")
        self.assertEqual(res_search.status_code, 200)
        self.assertTrue(any(item["booking_id"] == self.test_booking.ride_request_id for item in res_search.json()["items"]))

        # Status filter test
        res_status = self.client.get("/api/v1/admin/bookings?status=accepted")
        self.assertEqual(res_status.status_code, 200)
        self.assertTrue(all(item["status"] in ["accepted", "picked_up"] for item in res_status.json()["items"]))

    def test_03_get_admin_booking_details(self):
        res = self.client.get(f"/api/v1/admin/bookings/{self.test_booking.ride_request_id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["booking_id"], self.test_booking.ride_request_id)
        self.assertEqual(data["passenger"]["full_name"], "Booking Test Passenger")
        self.assertEqual(data["driver"]["full_name"], "Booking Test Driver")
        self.assertEqual(data["ride"]["source"], "Maradu")
        self.assertEqual(data["vehicle"]["brand"], "Maruti")

    def test_04_admin_cancel_booking_and_restore_seats(self):
        initial_available = self.test_ride.available_seats

        # Cancel with reason
        res_cancel = self.client.post(
            f"/api/v1/admin/bookings/{self.test_booking.ride_request_id}/cancel",
            json={"reason": "Emergency customer request to cancel"}
        )
        self.assertEqual(res_cancel.status_code, 200)
        data = res_cancel.json()
        self.assertEqual(data["status"], "cancelled")
        self.assertEqual(data["cancellation_reason"], "Emergency customer request to cancel")
        self.assertEqual(data["cancelled_by_admin"], "Booking Super Admin")

        # Verify seats were restored to the ride
        self.db.refresh(self.test_ride)
        self.assertEqual(self.test_ride.available_seats, initial_available + self.test_booking.seats_requested)

        # Repeated cancellation must be rejected
        res_repeat = self.client.post(
            f"/api/v1/admin/bookings/{self.test_booking.ride_request_id}/cancel",
            json={"reason": "Cancel again"}
        )
        self.assertEqual(res_repeat.status_code, 400)


if __name__ == "__main__":
    unittest.main()

