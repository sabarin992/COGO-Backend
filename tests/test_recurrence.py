import unittest
from datetime import date, time, timedelta
from app.models.recurring_ride import RecurrenceType
from app.services.recurrence_utils import calculate_recurrence_dates
from app.schemas.recurring_ride import RecurringRideCreate, RecurringRideUpdate
from pydantic import ValidationError


class TestRecurrenceLogic(unittest.TestCase):
    def test_once_recurrence(self):
        d = date(2026, 11, 1)
        dates = calculate_recurrence_dates(
            recurrence_type=RecurrenceType.ONCE,
            start_date=d,
            end_date=d + timedelta(days=7),
        )
        self.assertEqual(dates, [d])

    def test_daily_recurrence(self):
        # Nov 1, 2026 to Nov 7, 2026 -> 7 days
        start = date(2026, 11, 1)
        end = date(2026, 11, 7)
        dates = calculate_recurrence_dates(
            recurrence_type=RecurrenceType.DAILY,
            start_date=start,
            end_date=end,
        )
        self.assertEqual(len(dates), 7)
        self.assertEqual(dates[0], start)
        self.assertEqual(dates[-1], end)

    def test_weekdays_recurrence(self):
        # Nov 2, 2026 (Mon) to Nov 8, 2026 (Sun)
        # Should generate Mon, Tue, Wed, Thu, Fri (5 rides) and exclude Sat & Sun
        start = date(2026, 11, 2)  # Monday
        end = date(2026, 11, 8)    # Sunday
        dates = calculate_recurrence_dates(
            recurrence_type=RecurrenceType.WEEKDAYS,
            start_date=start,
            end_date=end,
        )
        self.assertEqual(len(dates), 5)
        for d in dates:
            self.assertIn(d.weekday(), [0, 1, 2, 3, 4])
            self.assertNotIn(d.weekday(), [5, 6])

    def test_shift_workdays_recurrence(self):
        # 2 working days, 2 off days
        # Day 1: Working (Nov 1)
        # Day 2: Working (Nov 2)
        # Day 3: Off (Nov 3)
        # Day 4: Off (Nov 4)
        # Day 5: Working (Nov 5)
        # Day 6: Working (Nov 6)
        # Day 7: Off (Nov 7)
        # Day 8: Off (Nov 8)
        start = date(2026, 11, 1)
        end = date(2026, 11, 8)
        dates = calculate_recurrence_dates(
            recurrence_type=RecurrenceType.SHIFT,
            start_date=start,
            end_date=end,
            working_days=2,
            off_days=2,
            shift_start_date=start,
        )
        expected = [
            date(2026, 11, 1),
            date(2026, 11, 2),
            date(2026, 11, 5),
            date(2026, 11, 6),
        ]
        self.assertEqual(dates, expected)

    def test_custom_weekdays_recurrence(self):
        # Select Mon (0), Wed (2), Fri (4)
        # Nov 2, 2026 (Mon) to Nov 15, 2026 (Sun) -> 2 weeks = 6 rides
        start = date(2026, 11, 2)
        end = date(2026, 11, 15)
        dates = calculate_recurrence_dates(
            recurrence_type=RecurrenceType.CUSTOM,
            start_date=start,
            end_date=end,
            selected_weekdays=[0, 2, 4],
        )
        self.assertEqual(len(dates), 6)
        for d in dates:
            self.assertIn(d.weekday(), [0, 2, 4])

    def test_custom_weekdays_string_names(self):
        start = date(2026, 11, 2)
        end = date(2026, 11, 8)
        dates = calculate_recurrence_dates(
            recurrence_type=RecurrenceType.CUSTOM,
            start_date=start,
            end_date=end,
            selected_weekdays=["monday", "wednesday", "friday"],
        )
        self.assertEqual(len(dates), 3)

    def test_validation_start_after_end(self):
        today = date.today()
        with self.assertRaises(ValidationError):
            RecurringRideCreate(
                vehicle_id=1,
                source="Maradu",
                destination="Edappally",
                available_seats=3,
                travel_time=time(8, 0),
                recurrence_type=RecurrenceType.DAILY,
                start_date=today + timedelta(days=10),
                end_date=today + timedelta(days=5),
            )

    def test_validation_past_start_date(self):
        past_date = date.today() - timedelta(days=2)
        with self.assertRaises(ValidationError):
            RecurringRideCreate(
                vehicle_id=1,
                source="Maradu",
                destination="Edappally",
                available_seats=3,
                travel_time=time(8, 0),
                recurrence_type=RecurrenceType.DAILY,
                start_date=past_date,
                end_date=date.today() + timedelta(days=5),
            )

    def test_validation_empty_custom_weekdays(self):
        today = date.today()
        with self.assertRaises(ValidationError):
            RecurringRideCreate(
                vehicle_id=1,
                source="Maradu",
                destination="Edappally",
                available_seats=3,
                travel_time=time(8, 0),
                recurrence_type=RecurrenceType.CUSTOM,
                start_date=today,
                end_date=today + timedelta(days=7),
                selected_weekdays=[],
            )

    def test_validation_invalid_shift_params(self):
        today = date.today()
        # Missing shift_start_date
        with self.assertRaises(ValidationError):
            RecurringRideCreate(
                vehicle_id=1,
                source="Maradu",
                destination="Edappally",
                available_seats=3,
                travel_time=time(8, 0),
                recurrence_type=RecurrenceType.SHIFT,
                start_date=today,
                end_date=today + timedelta(days=7),
                working_days=2,
                off_days=2,
                shift_start_date=None,
            )

        # 0 working days
        with self.assertRaises(ValidationError):
            RecurringRideCreate(
                vehicle_id=1,
                source="Maradu",
                destination="Edappally",
                available_seats=3,
                travel_time=time(8, 0),
                recurrence_type=RecurrenceType.SHIFT,
                start_date=today,
                end_date=today + timedelta(days=7),
                working_days=0,
                off_days=2,
                shift_start_date=today,
            )


if __name__ == "__main__":
    unittest.main()
