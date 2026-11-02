import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Prevent app.main from trying to connect to PostgreSQL during module import in tests
with patch("app.db.base.Base.metadata.create_all"):
    from app.main import app

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.api.deps import get_current_user_ws
from app.db.deps import get_db
from app.models.user import User
from app.models.ride import Ride, RideStatus
from app.models.ride_request import RideRequest
from app.websocket.location_manager import LocationManager


class DummyUser:
    def __init__(self, user_id: int, role: str = "rider", email: str = "test@example.com"):
        self.id = user_id
        self.role = role
        self.email = email
        self.full_name = f"User {user_id}"


class DummyRide:
    def __init__(self, ride_id: int, driver_id: int, status: str = "STARTED"):
        self.ride_id = ride_id
        self.driver_id = driver_id
        self.status = status


class DummyRideRequest:
    def __init__(self, request_id: int, ride_id: int, passenger_id: int, status: str = "accepted"):
        self.ride_request_id = request_id
        self.ride_id = ride_id
        self.passenger_id = passenger_id
        self.status = status


# --- Unit Tests for LocationManager ---

@pytest.mark.anyio
async def test_location_manager_lifecycle():
    manager = LocationManager()
    ws_mock1 = AsyncMock()
    ws_mock2 = AsyncMock()

    # Connect
    await manager.connect(ride_id=101, websocket=ws_mock1)
    await manager.connect(ride_id=101, websocket=ws_mock2)
    assert len(manager.active_connections[101]) == 2

    # Broadcast
    msg = {"type": "location", "lat": 12.97, "lng": 77.59}
    sent = await manager.broadcast(101, msg)
    assert sent == 2
    assert manager.get_last_location(101) == msg

    # Disconnect one
    manager.disconnect(101, ws_mock1)
    assert len(manager.active_connections[101]) == 1

    # Disconnect second -> room deleted
    manager.disconnect(101, ws_mock2)
    assert 101 not in manager.active_connections

    # Clear ride
    manager.clear_ride(101)
    assert manager.get_last_location(101) is None


# --- Endpoint Integration Tests using TestClient ---

def test_ws_ride_not_found():
    """Connecting to a non-existent ride should reject with code 1008."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    current_user = DummyUser(user_id=1)

    app.dependency_overrides[get_current_user_ws] = lambda: current_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)
    try:
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/api/v1/location/ws/99999"):
                pass
        assert exc_info.value.code == 1008
    finally:
        app.dependency_overrides.clear()


def test_ws_ride_inactive_status():
    """Connecting to a ride with CREATED or COMPLETED status should reject with code 1008."""
    dummy_ride = DummyRide(ride_id=200, driver_id=1, status="CREATED")

    mock_db = MagicMock()
    # get_ride_by_id_only uses db.query(Ride).filter(...)
    mock_db.query.return_value.filter.return_value.first.return_value = dummy_ride

    current_user = DummyUser(user_id=1)

    app.dependency_overrides[get_current_user_ws] = lambda: current_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)
    try:
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/api/v1/location/ws/200"):
                pass
        assert exc_info.value.code == 1008
    finally:
        app.dependency_overrides.clear()


def test_ws_unauthorized_user():
    """A user who is neither the driver nor has an accepted booking should be rejected."""
    dummy_ride = DummyRide(ride_id=201, driver_id=1, status="STARTED")

    mock_db = MagicMock()
    # First query is for Ride -> found
    # Second query is for RideRequest -> None (no accepted booking)
    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Ride:
            query_mock.filter.return_value.first.return_value = dummy_ride
        elif model == RideRequest:
            query_mock.filter.return_value.first.return_value = None
        return query_mock

    mock_db.query.side_effect = query_side_effect

    # User 5 is not driver (1) and not accepted passenger
    current_user = DummyUser(user_id=5)

    app.dependency_overrides[get_current_user_ws] = lambda: current_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)
    try:
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/api/v1/location/ws/201"):
                pass
        assert exc_info.value.code == 1008
    finally:
        app.dependency_overrides.clear()


def test_ws_driver_broadcast_and_passenger_receive():
    """Driver connects, sends coordinates; passenger connects and receives live location."""
    dummy_ride = DummyRide(ride_id=202, driver_id=1, status="STARTED")
    dummy_request = DummyRideRequest(request_id=10, ride_id=202, passenger_id=2, status="accepted")

    mock_db = MagicMock()
    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Ride:
            query_mock.filter.return_value.first.return_value = dummy_ride
        elif model == RideRequest:
            query_mock.filter.return_value.first.return_value = dummy_request
        return query_mock

    mock_db.query.side_effect = query_side_effect
    app.dependency_overrides[get_db] = lambda: mock_db

    driver_user = DummyUser(user_id=1)
    passenger_user = DummyUser(user_id=2)

    client = TestClient(app)

    try:
        # 1. Connect passenger
        app.dependency_overrides[get_current_user_ws] = lambda: passenger_user
        with client.websocket_connect("/api/v1/location/ws/202") as passenger_ws:

            # 2. Connect driver in another session
            app.dependency_overrides[get_current_user_ws] = lambda: driver_user
            with client.websocket_connect("/api/v1/location/ws/202") as driver_ws:
                # Driver sends GPS coordinates
                driver_ws.send_json({"lat": 12.9716, "lng": 77.5946})

                # Passenger receives broadcast
                received = passenger_ws.receive_json()
                assert received["type"] == "location"
                assert received["lat"] == 12.9716
                assert received["lng"] == 77.5946
                assert received["ride_id"] == 202
                assert "timestamp" in received
    finally:
        app.dependency_overrides.clear()


def test_ws_invalid_coordinate_payload():
    """Driver sending non-numeric coordinates receives an error frame without disconnecting."""
    dummy_ride = DummyRide(ride_id=203, driver_id=1, status="STARTED")

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = dummy_ride

    driver_user = DummyUser(user_id=1)
    app.dependency_overrides[get_current_user_ws] = lambda: driver_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)
    try:
        with client.websocket_connect("/api/v1/location/ws/203") as ws:
            # Send invalid lat
            ws.send_json({"lat": "invalid_num", "lng": 77.5946})
            err = ws.receive_json()
            assert err["type"] == "error"
            assert "numeric" in err["detail"]

            # Send out-of-range lat
            ws.send_json({"lat": 95.0, "lng": 77.5946})
            err2 = ws.receive_json()
            assert err2["type"] == "error"
            assert "-90 and 90" in err2["detail"]
    finally:
        app.dependency_overrides.clear()


def test_ws_pending_booking_rejected():
    """Passenger with status='pending' (not accepted or picked_up) must be rejected with 1008."""
    dummy_ride = DummyRide(ride_id=204, driver_id=1, status="STARTED")

    mock_db = MagicMock()
    # Query for RideRequest filters status.in_(["accepted", "picked_up"]) so it returns None for pending
    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Ride:
            query_mock.filter.return_value.first.return_value = dummy_ride
        elif model == RideRequest:
            query_mock.filter.return_value.first.return_value = None
        return query_mock

    mock_db.query.side_effect = query_side_effect
    passenger_user = DummyUser(user_id=3)

    app.dependency_overrides[get_current_user_ws] = lambda: passenger_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)
    try:
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/api/v1/location/ws/204"):
                pass
        assert exc_info.value.code == 1008
    finally:
        app.dependency_overrides.clear()


def test_ws_cached_location_on_passenger_connect():
    """When a driver has previously broadcast, a new connecting passenger gets cached location immediately."""
    from app.api.v1.endpoints.location import location_manager

    dummy_ride = DummyRide(ride_id=205, driver_id=1, status="STARTED")
    dummy_request = DummyRideRequest(request_id=11, ride_id=205, passenger_id=4, status="accepted")

    # Seed the location manager cache
    cached_loc = {
        "type": "location",
        "ride_id": 205,
        "lat": 13.0827,
        "lng": 80.2707,
        "timestamp": "2026-11-03T05:20:00Z",
    }
    location_manager.last_known_locations[205] = cached_loc

    mock_db = MagicMock()
    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Ride:
            query_mock.filter.return_value.first.return_value = dummy_ride
        elif model == RideRequest:
            query_mock.filter.return_value.first.return_value = dummy_request
        return query_mock

    mock_db.query.side_effect = query_side_effect

    passenger_user = DummyUser(user_id=4)
    app.dependency_overrides[get_current_user_ws] = lambda: passenger_user
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)
    try:
        with client.websocket_connect("/api/v1/location/ws/205") as ws:
            immediate_msg = ws.receive_json()
            assert immediate_msg["type"] == "location"
            assert immediate_msg["lat"] == 13.0827
            assert immediate_msg["lng"] == 80.2707
    finally:
        location_manager.clear_ride(205)
        app.dependency_overrides.clear()

