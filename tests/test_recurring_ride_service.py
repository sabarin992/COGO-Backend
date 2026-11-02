import unittest
from datetime import date, time, timedelta
from app.db.session import SessionLocal
from app.models.user import User
from app.models.kyc_docs import KYC
from app.models.vehicle import Vehicle
from app.models.ride import Ride, RideStatus
from app.models.recurring_ride import RecurringRide, RecurrenceType
from app.models.ride_request import RideRequest
from app.schemas.recurring_ride import RecurringRideCreate, RecurringRideUpdate
from app.services import recurring_ride_service
from app.repositories import recurring_ride_repo


class TestRecurringRideService(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        # Create a test rider user
        self.email = "test_rider_recurrence@example.com"
        existing_user = self.db.query(User).filter(User.email == self.email).first()
        if existing_user:
            self.user = existing_user
        else:
            self.user = User(
                full_name="Recurring Test Driver",
                email=self.email,
                phone="9876543210",
                role="rider",
                email_verified=True,
            )
            self.db.add(self.user)
            self.db.commit()
            self.db.refresh(self.user)

        # Create a test vehicle
        existing_veh = self.db.query(Vehicle).filter(Vehicle.user_id == self.user.id).first()
        if existing_veh:
            self.vehicle = existing_veh
        else:
            self.vehicle = Vehicle(
                user_id=self.user.id,
                vehicle_type="Car",
                brand="Hyundai",
                model="Creta",
                year=2024,
                color="Polar White",
                registration_number="KL-07-RECUR-9999",
                seating_capacity=4,
            )
            self.db.add(self.vehicle)
            self.db.commit()
            self.db.refresh(self.vehicle)

    def tearDown(self):
        # Cleanup created recurring rides and rides
        created_recurrings = self.db.query(RecurringRide).filter(RecurringRide.driver_id == self.user.id).all()
        for rec in created_recurrings:
            self.db.delete(rec)
        self.db.commit()
        self.db.close()

    def test_create_daily_recurring_ride_and_generation(self):
        today = date.today()
        start = today + timedelta(days=1)
        end = today + timedelta(days=5)

        data = RecurringRideCreate(
            vehicle_id=self.vehicle.id,
            source="Maradu",
            destination="Edappally",
            available_seats=3,
            travel_time=time(8, 0),
            recurrence_type=RecurrenceType.DAILY,
            start_date=start,
            end_date=end,
        )

        res = recurring_ride_service.create_recurring_ride(self.db, data, self.email)
        self.assertEqual(res.recurrence_type, "DAILY")
        self.assertEqual(res.total_rides, 5)
        self.assertEqual(len(res.rides), 5)

        # Verify database records
        db_rides = self.db.query(Ride).filter(Ride.recurring_ride_id == res.id).all()
        self.assertEqual(len(db_rides), 5)
        for r in db_rides:
            self.assertEqual(r.driver_id, self.user.id)
            self.assertEqual(r.vehicle_id, self.vehicle.id)
            self.assertEqual(r.source, "Maradu")
            self.assertEqual(r.available_seats, 3)

    def test_duplicate_prevention_idempotency(self):
        today = date.today()
        start = today + timedelta(days=1)
        end = today + timedelta(days=3)

        data = RecurringRideCreate(
            vehicle_id=self.vehicle.id,
            source="Kaloor",
            destination="Infopark",
            available_seats=2,
            travel_time=time(9, 30),
            recurrence_type=RecurrenceType.DAILY,
            start_date=start,
            end_date=end,
        )

        res = recurring_ride_service.create_recurring_ride(self.db, data, self.email)
        self.assertEqual(res.total_rides, 3)

        # Calling generate_rides_for_schedule again should create 0 new rides
        rec_model = recurring_ride_repo.get_recurring_ride_by_id(self.db, res.id)
        new_cnt = recurring_ride_service.generate_rides_for_schedule(self.db, rec_model)
        self.assertEqual(new_cnt, 0)

        total_rides = self.db.query(Ride).filter(Ride.recurring_ride_id == res.id).count()
        self.assertEqual(total_rides, 3)

    def test_pause_and_resume_schedule(self):
        today = date.today()
        start = today + timedelta(days=1)
        end = today + timedelta(days=4)

        data = RecurringRideCreate(
            vehicle_id=self.vehicle.id,
            source="Vytilla",
            destination="Aluva",
            available_seats=3,
            travel_time=time(7, 45),
            recurrence_type=RecurrenceType.DAILY,
            start_date=start,
            end_date=end,
        )
        res = recurring_ride_service.create_recurring_ride(self.db, data, self.email)
        self.assertTrue(res.is_active)

        # Pause
        paused = recurring_ride_service.pause_recurring_ride_service(self.db, res.id, self.email)
        self.assertFalse(paused.is_active)
        self.assertEqual(paused.schedule_status, "Paused")

        # Resume
        resumed = recurring_ride_service.resume_recurring_ride_service(self.db, res.id, self.email)
        self.assertTrue(resumed.is_active)
        self.assertEqual(resumed.schedule_status, "Active")

    def test_edit_schedule_preserves_booked_rides(self):
        today = date.today()
        start = today + timedelta(days=1)
        end = today + timedelta(days=3)

        data = RecurringRideCreate(
            vehicle_id=self.vehicle.id,
            source="Fort Kochi",
            destination="Marine Drive",
            available_seats=3,
            travel_time=time(10, 0),
            recurrence_type=RecurrenceType.DAILY,
            start_date=start,
            end_date=end,
        )
        res = recurring_ride_service.create_recurring_ride(self.db, data, self.email)
        rides = self.db.query(Ride).filter(Ride.recurring_ride_id == res.id).order_by(Ride.travel_date).all()
        first_ride = rides[0]

        # Simulate a passenger booking on the first ride
        fake_passenger = User(
            full_name="Test Passenger",
            email="test_passenger_recur@example.com",
            phone="9123456780",
            role="consumer",
        )
        self.db.add(fake_passenger)
        self.db.commit()
        self.db.refresh(fake_passenger)

        req = RideRequest(
            ride_id=first_ride.ride_id,
            passenger_id=fake_passenger.id,
            seats_requested=1,
            status="accepted",
        )
        self.db.add(req)
        self.db.commit()

        # Now edit recurring schedule: change travel_time and destination
        update = RecurringRideUpdate(
            destination="MG Road Metro",
            travel_time=time(11, 30),
        )
        updated_res = recurring_ride_service.update_recurring_ride_service(
            self.db, res.id, update, self.email
        )

        # Check: the first ride (with booking) keeps its original destination and time!
        self.db.refresh(first_ride)
        self.assertEqual(first_ride.destination, "Marine Drive")
        self.assertEqual(first_ride.travel_time, time(10, 0))

        # Check: the other unbooked rides are updated to the new destination and time!
        unbooked_rides = [r for r in rides if r.ride_id != first_ride.ride_id]
        for ubr in unbooked_rides:
            self.db.refresh(ubr)
            self.assertEqual(ubr.destination, "MG Road Metro")
            self.assertEqual(ubr.travel_time, time(11, 30))

        # Cleanup passenger
        self.db.delete(req)
        self.db.delete(fake_passenger)
        self.db.commit()

    def test_individual_ride_deletion_preserves_schedule(self):
        today = date.today()
        start = today + timedelta(days=1)
        end = today + timedelta(days=3)

        data = RecurringRideCreate(
            vehicle_id=self.vehicle.id,
            source="Kakkanad",
            destination="Palarivattom",
            available_seats=2,
            travel_time=time(8, 30),
            recurrence_type=RecurrenceType.DAILY,
            start_date=start,
            end_date=end,
        )
        res = recurring_ride_service.create_recurring_ride(self.db, data, self.email)
        rides = self.db.query(Ride).filter(Ride.recurring_ride_id == res.id).all()
        self.assertEqual(len(rides), 3)

        # Delete one ride
        first_ride = rides[0]
        self.db.delete(first_ride)
        self.db.commit()

        # Schedule must still exist!
        schedule = recurring_ride_repo.get_recurring_ride_by_id(self.db, res.id)
        self.assertIsNotNone(schedule)
        remaining_rides = self.db.query(Ride).filter(Ride.recurring_ride_id == res.id).all()
        self.assertEqual(len(remaining_rides), 2)


if __name__ == "__main__":
    unittest.main()
