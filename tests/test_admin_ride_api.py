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


class TestAdminRideAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls.admin_email = "test_super_admin@example.com"
        cls.driver_email = "test_admin_driver@example.com"
        cls.passenger_email = "test_admin_passenger@example.com"

        # Create Admin
        existing_admin = cls.db.query(User).filter(User.email == cls.admin_email).first()
        if existing_admin:
            cls.admin = existing_admin
            cls.admin.role = "admin"
            cls.db.commit()
        else:
            cls.admin = User(
                full_name="Super Admin",
                email=cls.admin_email,
                phone="9999900001",
                role="admin",
                email_verified=True,
            )
            cls.db.add(cls.admin)
            cls.db.commit()
            cls.db.refresh(cls.admin)

        # Create Driver
        existing_driver = cls.db.query(User).filter(User.email == cls.driver_email).first()
        if existing_driver:
            cls.driver = existing_driver
        else:
            cls.driver = User(
                full_name="Admin Test Driver",
                email=cls.driver_email,
                phone="9999900002",
                role="rider",
                email_verified=True,
            )
            cls.db.add(cls.driver)
            cls.db.commit()
            cls.db.refresh(cls.driver)

        # Create Passenger
        existing_pax = cls.db.query(User).filter(User.email == cls.passenger_email).first()
        if existing_pax:
            cls.passenger = existing_pax
        else:
            cls.passenger = User(
                full_name="Admin Test Passenger",
                email=cls.passenger_email,
                phone="9999900003",
                role="consumer",
                email_verified=True,
            )
            cls.db.add(cls.passenger)
            cls.db.commit()
            cls.db.refresh(cls.passenger)

        # Create Vehicle
        existing_veh = cls.db.query(Vehicle).filter(Vehicle.user_id == cls.driver.id).first()
        if existing_veh:
            cls.vehicle = existing_veh
        else:
            cls.vehicle = Vehicle(
                user_id=cls.driver.id,
                vehicle_type="Car",
                brand="Hyundai",
                model="Creta",
                year=2024,
                color="Black",
                registration_number="KL-07-ADM-9999",
                seating_capacity=4,
            )
            cls.db.add(cls.vehicle)
            cls.db.commit()
            cls.db.refresh(cls.vehicle)

        # Create Test Ride
        cls.test_ride = Ride(
            driver_id=cls.driver.id,
            vehicle_id=cls.vehicle.id,
            source="Kochi Infopark",
            destination="Ernakulam South",
            route="Via Seaport-Airport Rd",
            travel_date=date.today() + timedelta(days=2),
            travel_time=time(9, 30),
            available_seats=3,
            status=RideStatus.CREATED.value,
        )
        cls.db.add(cls.test_ride)
        cls.db.commit()
        cls.db.refresh(cls.test_ride)

        # Create Ride Request
        cls.test_request = RideRequest(
            ride_id=cls.test_ride.ride_id,
            passenger_id=cls.passenger.id,
            seats_requested=1,
            status="pending",
        )
        cls.db.add(cls.test_request)
        cls.db.commit()
        cls.db.refresh(cls.test_request)

        # Dependency override
        app.dependency_overrides[get_current_admin] = lambda: cls.admin
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        # Clean up test records
        try:
            cls.db.query(RideRequest).filter(RideRequest.ride_id == cls.test_ride.ride_id).delete()
            cls.db.query(Ride).filter(Ride.ride_id == cls.test_ride.ride_id).delete()
            cls.db.commit()
        except Exception:
            cls.db.rollback()
        cls.db.close()

    def test_01_get_admin_ride_statistics(self):
        res = self.client.get("/api/v1/admin/rides/statistics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total", data)
        self.assertIn("created", data)
        self.assertIn("upcoming", data)
        self.assertIn("cancelled", data)
        self.assertGreaterEqual(data["total"], 1)

    def test_02_get_admin_rides_list(self):
        res = self.client.get("/api/v1/admin/rides?page=1&size=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertIn("pages", data)
        self.assertGreaterEqual(len(data["items"]), 1)

        # Test search filter
        res_search = self.client.get("/api/v1/admin/rides?search=Infopark")
        self.assertEqual(res_search.status_code, 200)
        search_data = res_search.json()
        self.assertTrue(any(item["ride_id"] == self.test_ride.ride_id for item in search_data["items"]))

        # Test status filter
        res_filter = self.client.get("/api/v1/admin/rides?status=CREATED")
        self.assertEqual(res_filter.status_code, 200)
        filter_data = res_filter.json()
        self.assertTrue(all(item["status"] == "CREATED" for item in filter_data["items"]))

    def test_03_get_admin_ride_details(self):
        res = self.client.get(f"/api/v1/admin/rides/{self.test_ride.ride_id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["ride_id"], self.test_ride.ride_id)
        self.assertEqual(data["source"], "Kochi Infopark")
        self.assertIn("driver", data)
        self.assertEqual(data["driver"]["full_name"], "Admin Test Driver")
        self.assertIn("vehicle", data)
        self.assertEqual(data["vehicle"]["brand"], "Hyundai")
        self.assertIn("requests", data)
        self.assertGreaterEqual(len(data["requests"]), 1)

    def test_04_admin_cancel_ride(self):
        # Mandatory reason validation
        res_bad = self.client.post(f"/api/v1/admin/rides/{self.test_ride.ride_id}/cancel", json={"reason": ""})
        self.assertEqual(res_bad.status_code, 422)  # pydantic min_length=1

        # Cancel ride with valid reason
        res_cancel = self.client.post(
            f"/api/v1/admin/rides/{self.test_ride.ride_id}/cancel",
            json={"reason": "Driver vehicle broke down - safety precaution"}
        )
        self.assertEqual(res_cancel.status_code, 200)
        data = res_cancel.json()
        self.assertEqual(data["status"], "CANCELLED")
        self.assertEqual(data["cancellation_reason"], "Driver vehicle broke down - safety precaution")
        self.assertEqual(data["cancelled_by_admin"], "Super Admin")

        # Verify associated ride request is marked as cancelled
        for req in data["requests"]:
            self.assertEqual(req["status"], "cancelled")

        # Try to cancel again - should fail
        res_repeat = self.client.post(
            f"/api/v1/admin/rides/{self.test_ride.ride_id}/cancel",
            json={"reason": "Cancel again"}
        )
        self.assertEqual(res_repeat.status_code, 400)


if __name__ == "__main__":
    unittest.main()

