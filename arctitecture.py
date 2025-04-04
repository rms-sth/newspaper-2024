import asyncio
import re
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Callable, Any, Union, Awaitable

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("event_system")


class Event:
    """Base class for all events"""

    def __init__(self, name: str, data: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.data = data or {}
        self.timestamp = datetime.now()
        self.propagation_stopped = False

    def stop_propagation(self):
        """Stop this event from being processed by further handlers"""
        self.propagation_stopped = True

    def __str__(self):
        return f"Event(name={self.name}, id={self.id}, timestamp={self.timestamp})"


class SystemEvent(Event):
    """Base class for system events"""

    def __init__(self, name: str, data: Dict[str, Any] = None):
        if not name.startswith("system."):
            name = f"system.{name}"
        super().__init__(name, data)


class UserEvent(Event):
    """Base class for user-initiated events"""

    def __init__(self, name: str, data: Dict[str, Any] = None):
        if not name.startswith("user."):
            name = f"user.{name}"
        super().__init__(name, data)


class ErrorEvent(Event):
    """Base class for error events"""

    def __init__(self, name: str, data: Dict[str, Any] = None):
        if not name.startswith("error."):
            name = f"error.{name}"
        data = data or {}
        if "message" not in data:
            data["message"] = "An error occurred"
        super().__init__(name, data)


class EventFilter:
    """Filter for event handlers"""

    def __init__(self, pattern: str = None, condition: Callable[[Event], bool] = None):
        self.pattern = None
        if pattern:
            # Convert wildcard patterns to regex
            regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
            self.pattern = re.compile(f"^{regex_pattern}$")
        self.condition = condition

    def matches(self, event: Event) -> bool:
        """Check if an event matches this filter"""
        if self.pattern and not self.pattern.match(event.name):
            return False
        if self.condition and not self.condition(event):
            return False
        return True


class EventHandler:
    """Handler for events"""

    def __init__(
        self,
        callback: Union[Callable[[Event], Any], Callable[[Event], Awaitable[Any]]],
        filter_: EventFilter,
        is_async: bool = False,
        priority: int = 0,
    ):
        self.callback = callback
        self.filter = filter_
        self.is_async = is_async
        self.priority = priority
        self.id = str(uuid.uuid4())

    def matches(self, event: Event) -> bool:
        """Check if this handler should process the given event"""
        return self.filter.matches(event)


class EventBus:
    """Central event dispatcher"""

    def __init__(self):
        self.handlers: List[EventHandler] = []
        self.metrics: Dict[str, int] = {"total_events": 0}
        self.event_history: List[Event] = []
        self.max_history_size = 100

    def register_handler(
        self,
        callback: Union[Callable[[Event], Any], Callable[[Event], Awaitable[Any]]],
        pattern: str = None,
        condition: Callable[[Event], bool] = None,
        is_async: bool = False,
        priority: int = 0,
    ) -> str:
        """Register an event handler"""
        filter_ = EventFilter(pattern, condition)
        handler = EventHandler(callback, filter_, is_async, priority)
        self.handlers.append(handler)
        # Sort handlers by priority (higher first)
        self.handlers.sort(key=lambda h: -h.priority)
        logger.info(f"Registered handler {handler.id} for pattern '{pattern}'")
        return handler.id

    def handler(self, pattern: str = None, is_async: bool = False, priority: int = 0):
        """Decorator for registering event handlers"""

        def decorator(func):
            self.register_handler(func, pattern, is_async=is_async, priority=priority)
            return func

        return decorator

    def async_handler(self, pattern: str = None, priority: int = 0):
        """Decorator for registering async event handlers"""
        return self.handler(pattern, is_async=True, priority=priority)

    def unregister_handler(self, handler_id: str) -> bool:
        """Unregister a handler by ID"""
        original_count = len(self.handlers)
        self.handlers = [h for h in self.handlers if h.id != handler_id]
        removed = len(self.handlers) < original_count
        if removed:
            logger.info(f"Unregistered handler {handler_id}")
        return removed

    def dispatch(self, event: Event) -> None:
        """Synchronously dispatch an event to all matching handlers"""
        self._record_event(event)
        logger.debug(f"Dispatching event: {event}")

        for handler in self.handlers:
            if event.propagation_stopped:
                break

            if not handler.matches(event):
                continue

            try:
                if handler.is_async:
                    # For async handlers in sync dispatch, we run them in the background
                    asyncio.create_task(handler.callback(event))
                else:
                    handler.callback(event)
            except Exception as e:
                logger.error(f"Error in event handler {handler.id}: {e}")
                self.dispatch(
                    ErrorEvent(
                        "error.handler",
                        {
                            "message": f"Handler error: {str(e)}",
                            "handler_id": handler.id,
                            "event_id": event.id,
                        },
                    )
                )

    async def dispatch_async(self, event: Event) -> None:
        """Asynchronously dispatch an event to all matching handlers"""
        self._record_event(event)
        logger.debug(f"Async dispatching event: {event}")

        for handler in self.handlers:
            if event.propagation_stopped:
                break

            if not handler.matches(event):
                continue

            try:
                if handler.is_async:
                    await handler.callback(event)
                else:
                    # For sync handlers in async dispatch, we run them directly
                    handler.callback(event)
            except Exception as e:
                logger.error(f"Error in event handler {handler.id}: {e}")
                await self.dispatch_async(
                    ErrorEvent(
                        "error.handler",
                        {
                            "message": f"Handler error: {str(e)}",
                            "handler_id": handler.id,
                            "event_id": event.id,
                        },
                    )
                )

    def _record_event(self, event: Event) -> None:
        """Record event for metrics and history"""
        self.metrics["total_events"] = self.metrics.get("total_events", 0) + 1
        event_type = event.name.split(".")[0]
        self.metrics[f"events_{event_type}"] = (
            self.metrics.get(f"events_{event_type}", 0) + 1
        )

        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)

    def delay_event(self, event: Event, delay_seconds: float) -> None:
        """Schedule an event to be dispatched after a delay"""

        def delayed_dispatch():
            time.sleep(delay_seconds)
            self.dispatch(event)

        import threading

        thread = threading.Thread(target=delayed_dispatch)
        thread.daemon = True
        thread.start()
        logger.debug(
            f"Scheduled event {event.id} for dispatch in {delay_seconds} seconds"
        )

    async def delay_event_async(self, event: Event, delay_seconds: float) -> None:
        """Schedule an event to be dispatched asynchronously after a delay"""
        await asyncio.sleep(delay_seconds)
        await self.dispatch_async(event)
        logger.debug(
            f"Scheduled event {event.id} for async dispatch in {delay_seconds} seconds"
        )

    def get_metrics(self) -> Dict[str, int]:
        """Get event metrics"""
        return self.metrics.copy()


class EventEmitter:
    """Mixin class that allows any class to emit events"""

    def register_event_bus(self, event_bus: EventBus) -> None:
        """Register an event bus for this emitter"""
        self._event_bus = event_bus

    def emit(self, event_name: str, data: Dict[str, Any] = None) -> Event:
        """Emit an event to the registered event bus"""
        if not hasattr(self, "_event_bus"):
            raise RuntimeError("No event bus registered for this emitter")

        event = Event(event_name, data)
        self._event_bus.dispatch(event)
        return event

    async def emit_async(self, event_name: str, data: Dict[str, Any] = None) -> Event:
        """Emit an event asynchronously to the registered event bus"""
        if not hasattr(self, "_event_bus"):
            raise RuntimeError("No event bus registered for this emitter")

        event = Event(event_name, data)
        await self._event_bus.dispatch_async(event)
        return event

    def emit_delayed(
        self, event_name: str, data: Dict[str, Any] = None, delay_seconds: float = 1.0
    ) -> Event:
        """Emit an event after a delay"""
        if not hasattr(self, "_event_bus"):
            raise RuntimeError("No event bus registered for this emitter")

        event = Event(event_name, data)
        self._event_bus.delay_event(event, delay_seconds)
        return event


# Example implementation of a user authenticator using the EventEmitter mixin
class UserAuthenticator(EventEmitter):
    def __init__(self, event_bus):
        self.register_event_bus(event_bus)
        self.users = {"admin": "password123", "guest": "guest"}

    def authenticate(self, username, password):
        """Authenticate a user and emit appropriate events"""
        if self._check_credentials(username, password):
            self.emit("user.login", {"username": username})
            return True
        else:
            self.emit(
                "error.authentication",
                {"message": "Invalid credentials", "username": username},
            )
            return False

    def _check_credentials(self, username, password):
        """Check if the provided credentials are valid"""
        return username in self.users and self.users[username] == password


# A service that uses the EventEmitter mixin
class NotificationService(EventEmitter):
    def __init__(self, event_bus):
        self.register_event_bus(event_bus)
        self.notifications = []

    def send_notification(self, user_id, message):
        print(f"Sending notification to user {user_id}: {message}")
        self.notifications.append({"user_id": user_id, "message": message})
        self.emit(
            "notification.sent",
            {"user_id": user_id, "message": message, "timestamp": time.time()},
        )

    async def send_notification_async(self, user_id, message):
        print(f"Async sending notification to user {user_id}: {message}")
        self.notifications.append({"user_id": user_id, "message": message})
        await self.emit_async(
            "notification.sent",
            {"user_id": user_id, "message": message, "timestamp": time.time()},
        )


# A more complex user service
class UserService(EventEmitter):
    def __init__(self, event_bus):
        self.register_event_bus(event_bus)
        self.users = {}
        self.logged_in_users = set()

    def create_user(self, user_id, username, email):
        if user_id in self.users:
            self.emit(
                "error.user",
                {"message": f"User {user_id} already exists", "user_id": user_id},
            )
            return False

        self.users[user_id] = {
            "username": username,
            "email": email,
            "created_at": time.time(),
        }

        self.emit("user.created", {"user_id": user_id, "username": username})
        return True

    def login(self, user_id):
        if user_id not in self.users:
            self.emit(
                "error.authentication",
                {"message": f"User {user_id} does not exist", "user_id": user_id},
            )
            return False

        self.logged_in_users.add(user_id)
        self.emit(
            "user.login",
            {"user_id": user_id, "username": self.users[user_id]["username"]},
        )
        return True

    def logout(self, user_id):
        if user_id not in self.logged_in_users:
            return False

        self.logged_in_users.remove(user_id)
        self.emit(
            "user.logout",
            {"user_id": user_id, "username": self.users[user_id]["username"]},
        )
        return True


# AsyncEventProcessor to demonstrate async event handling
class AsyncEventProcessor:
    def __init__(self, event_bus):
        self.event_bus = event_bus

        @event_bus.async_handler("user.*")
        async def async_user_event_handler(event):
            print(f"Processing user event asynchronously: {event.name}")
            await asyncio.sleep(1)  # Simulate async processing
            print(f"Finished processing {event.name}")

    async def process_events(self):
        # Create and dispatch some events asynchronously
        print("Starting async event processing...")

        events = [
            UserEvent("profile.updated", {"user_id": "1", "field": "email"}),
            UserEvent("settings.changed", {"user_id": "1", "theme": "dark"}),
            SystemEvent("cache.cleared", {"component": "user_service"}),
        ]

        for event in events:
            await self.event_bus.dispatch_async(event)
            await asyncio.sleep(0.5)

        print("Finished dispatching async events")


# Event monitoring and analysis
class EventMonitor:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_counts = {}
        self.setup_handlers()

    def setup_handlers(self):
        # Global handler to monitor all events
        @self.event_bus.handler("*", priority=-100)  # Low priority to run last
        def monitor_all_events(event):
            event_type = event.name.split(".")[0]
            self.event_counts[event.name] = self.event_counts.get(event.name, 0) + 1
            self.event_counts[f"{event_type}.*"] = (
                self.event_counts.get(f"{event_type}.*", 0) + 1
            )

    def print_report(self):
        print("\n--- Event Monitor Report ---")
        print(f"Total events tracked: {sum(self.event_counts.values())}")
        print("Event counts by type:")
        for event_name, count in sorted(self.event_counts.items()):
            print(f"  {event_name}: {count}")
        print("-------------------------")


# Simple demo application
# The issue is in the SimpleEventDrivenApp.setup_handlers() method
# Here's how to fix it:


class SimpleEventDrivenApp:
    def __init__(self):
        self.event_bus = EventBus()
        self.user_auth = UserAuthenticator(self.event_bus)
        self.setup_handlers()

    def setup_handlers(self):
        # Register event handlers
        @self.event_bus.handler("user.login")
        def on_user_login(event):
            print(f"User logged in: {event.data['username']}")

        @self.event_bus.handler("system.startup")
        def on_system_startup(event):
            print(f"System started at {event.timestamp}")

        @self.event_bus.handler("error.*")  # Wildcard pattern
        def on_any_error(event):
            print(f"Error occurred: {event.name} - {event.data['message']}")

        # High-priority handler for security events
        @self.event_bus.handler("security.*", priority=10)
        def on_security_event(event):
            print(f"SECURITY ALERT: {event.name}")

        # Handler with custom condition
        # The issue is here - we need to pass the condition separately
        def admin_condition(event):
            return event.data.get("username") == "admin"

        @self.event_bus.handler("user.*")
        def on_admin_action(event):
            if admin_condition(event):
                print(f"Admin action: {event.name}")

    def run(self):
        print("Starting simple event-driven application demo...")

        # Emit system startup event
        self.event_bus.dispatch(
            SystemEvent("startup", {"version": "1.0", "environment": "development"})
        )

        # Try authentication
        self.user_auth.authenticate("admin", "password123")  # Successful
        self.user_auth.authenticate("guest", "wrongpass")  # Failed

        # Emit a delayed event
        print("Scheduling delayed event...")
        self.event_bus.delay_event(
            UserEvent("notification", {"message": "This is a delayed notification"}),
            2.0,
        )

        # Wait for delayed event
        time.sleep(3)

        # Show metrics
        print("\nEvent metrics:")
        for key, value in self.event_bus.get_metrics().items():
            print(f"  {key}: {value}")


# Complex demo with async features
async def run_complex_demo():
    event_bus = EventBus()

    # Create services
    user_service = UserService(event_bus)
    notification_service = NotificationService(event_bus)
    event_monitor = EventMonitor(event_bus)
    async_processor = AsyncEventProcessor(event_bus)

    # Set up event handlers
    @event_bus.handler("user.created")
    def on_user_created(event):
        user_id = event.data["user_id"]
        username = event.data["username"]
        print(f"New user created: {username} (ID: {user_id})")
        notification_service.send_notification(
            user_id, f"Welcome, {username}! Your account has been created."
        )

    @event_bus.handler("user.login")
    def on_user_login(event):
        user_id = event.data.get("user_id")
        username = event.data.get("username")
        if user_id and username:
            print(f"User logged in: {username} (ID: {user_id})")
        elif "username" in event.data:
            print(f"User logged in: {event.data['username']}")

    @event_bus.handler("notification.sent")
    def on_notification_sent(event):
        user_id = event.data["user_id"]
        print(f"Notification confirmed for user {user_id}")

    @event_bus.handler("error.*")
    def on_error(event):
        print(f"ERROR: {event.data['message']}")

    # Create some test events
    print("\n--- Starting Complex Event Demo ---")

    # Create users
    user_service.create_user("1", "alice", "alice@example.com")
    user_service.create_user("2", "bob", "bob@example.com")
    user_service.create_user("1", "duplicate", "duplicate@example.com")  # Should fail

    # Login users
    user_service.login("1")
    user_service.login("2")
    user_service.login("3")  # Should fail

    # Send direct notification
    notification_service.send_notification("2", "You have a new message")

    # Schedule a delayed event
    event_bus.delay_event(
        SystemEvent("maintenance", {"scheduled": time.time() + 60}), 2.0
    )

    # Run async event processing
    await async_processor.process_events()

    # Logout users
    user_service.logout("1")

    # Allow time for delayed events
    await asyncio.sleep(3)

    # Print event metrics
    event_monitor.print_report()
    print("\n--- Complex Event Demo Complete ---")


# Main function to run all the demos
async def main():
    # Run the simple demo
    simple_app = SimpleEventDrivenApp()
    simple_app.run()

    # Run the complex demo with async features
    await run_complex_demo()


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
