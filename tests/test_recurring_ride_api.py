import unittest
from datetime import date, time, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.kyc_docs import KYC
from app.models.vehicle import Vehicle
from app.models.ride import Ride
from app.models.recurring_ride import RecurringRide, RecurrenceType
from app.api.deps import get_current_user


class TestRecurringRideAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls.email = "test_api_driver@example.com"
        # Create test user
        existing_user = cls.db.query(User).filter(User.email == cls.email).first()
        if existing_user:
            cls.user = existing_user
        else:
            cls.user = User(
                full_name="API Test Rider",
                email=cls.email,
                phone="9876000001",
                role="rider",
                email_verified=True,
            )
            cls.db.add(cls.user)
            cls.db.commit()
            cls.db.refresh(cls.user)

        # Create test vehicle
        existing_veh = cls.db.query(Vehicle).filter(Vehicle.user_id == cls.user.id).first()
        if existing_veh:
            cls.vehicle = existing_veh
        else:
            cls.vehicle = Vehicle(
                user_id=cls.user.id,
                vehicle_type="Car",
                brand="Honda",
                model="City",
                year=2023,
                color="Silver",
                registration_number="KL-07-API-8888",
                seating_capacity=4,
            )
            cls.db.add(cls.vehicle)
            cls.db.commit()
            cls.db.refresh(cls.vehicle)

        # Override dependency
        app.dependency_overrides[get_current_user] = lambda: cls.email
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        created_recurrings = cls.db.query(RecurringRide).filter(RecurringRide.driver_id == cls.user.id).all()
        for rec in created_recurrings:
            cls.db.delete(rec)
        cls.db.commit()
        cls.db.close()

    def test_full_api_lifecycle(self):
        today = date.today()
        start = today + timedelta(days=1)
        end = today + timedelta(days=5)

        # 1. POST /api/v1/recurring-rides
        payload = {
            "vehicle_id": self.vehicle.id,
            "source": "Aluva Metro",
            "destination": "MG Road",
            "available_seats": 3,
            "travel_time": "08:30:00",
            "recurrence_type": "DAILY",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }

        create_res = self.client.post("/api/v1/recurring-rides/", json=payload)
        self.assertEqual(create_res.status_code, 201, create_res.text)
        created_data = create_res.json()
        rec_id = created_data["id"]
        self.assertEqual(created_data["recurrence_type"], "DAILY")
        self.assertEqual(created_data["total_rides"], 5)
        self.assertEqual(len(created_data["rides"]), 5)

        # 2. GET /api/v1/recurring-rides
        list_res = self.client.get("/api/v1/recurring-rides/")
        self.assertEqual(list_res.status_code, 200)
        items = list_res.json()
        self.assertTrue(any(item["id"] == rec_id for item in items))

        # 3. GET /api/v1/recurring-rides/{id}
        get_res = self.client.get(f"/api/v1/recurring-rides/{rec_id}")
        self.assertEqual(get_res.status_code, 200)
        detail_data = get_res.json()
        self.assertEqual(detail_data["id"], rec_id)
        self.assertEqual(len(detail_data["rides"]), 5)

        # 4. PATCH /api/v1/recurring-rides/{id}/pause
        pause_res = self.client.patch(f"/api/v1/recurring-rides/{rec_id}/pause")
        self.assertEqual(pause_res.status_code, 200)
        self.assertFalse(pause_res.json()["is_active"])
        self.assertEqual(pause_res.json()["schedule_status"], "Paused")

        # 5. PATCH /api/v1/recurring-rides/{id}/resume
        resume_res = self.client.patch(f"/api/v1/recurring-rides/{rec_id}/resume")
        self.assertEqual(resume_res.status_code, 200)
        self.assertTrue(resume_res.json()["is_active"])
        self.assertEqual(resume_res.json()["schedule_status"], "Active")

        # 6. PUT /api/v1/recurring-rides/{id} (update available seats & departure time)
        update_payload = {
            "available_seats": 2,
            "travel_time": "09:00:00",
        }
        put_res = self.client.put(f"/api/v1/recurring-rides/{rec_id}", json=update_payload)
        self.assertEqual(put_res.status_code, 200)
        updated_data = put_res.json()
        self.assertEqual(updated_data["available_seats"], 2)

        # Verify associated unbooked rides were updated
        for r in updated_data["rides"]:
            self.assertEqual(r["available_seats"], 2)
            self.assertEqual(r["travel_time"], "09:00:00")

        # 7. DELETE /api/v1/recurring-rides/{id}
        del_res = self.client.delete(f"/api/v1/recurring-rides/{rec_id}")
        self.assertEqual(del_res.status_code, 200)

        # Verify 404 after deletion
        get_deleted = self.client.get(f"/api/v1/recurring-rides/{rec_id}")
        self.assertEqual(get_deleted.status_code, 404)


if __name__ == "__main__":
    unittest.main()
