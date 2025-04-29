"""
Sample implementations of the Command pattern in Python.

The Command pattern encapsulates a request as an object, allowing users to
parameterize clients with different requests, queue or log requests, and
support undoable operations.
"""

# Implementation 1: Classic Command Pattern
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class Command(ABC):
    """Abstract command interface."""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command execution."""
        pass


class LightOnCommand(Command):
    """Concrete command for turning on a light."""
    
    def __init__(self, light):
        """Initialize with a light receiver."""
        self.light = light
    
    def execute(self) -> None:
        """Turn on the light."""
        self.light.turn_on()
    
    def undo(self) -> None:
        """Undo by turning off the light."""
        self.light.turn_off()


class LightOffCommand(Command):
    """Concrete command for turning off a light."""
    
    def __init__(self, light):
        """Initialize with a light receiver."""
        self.light = light
    
    def execute(self) -> None:
        """Turn off the light."""
        self.light.turn_off()
    
    def undo(self) -> None:
        """Undo by turning on the light."""
        self.light.turn_on()


class Light:
    """Receiver class that performs the actual actions."""
    
    def __init__(self, name: str):
        """Initialize with a name."""
        self.name = name
        self.is_on = False
    
    def turn_on(self) -> None:
        """Turn on the light."""
        self.is_on = True
        print(f"{self.name} light is now ON")
    
    def turn_off(self) -> None:
        """Turn off the light."""
        self.is_on = False
        print(f"{self.name} light is now OFF")


class RemoteControl:
    """Invoker class that asks the command to carry out the request."""
    
    def __init__(self):
        """Initialize with empty command slots."""
        self.on_commands: Dict[int, Command] = {}
        self.off_commands: Dict[int, Command] = {}
        self.undo_command: Optional[Command] = None
    
    def set_command(self, slot: int, on_command: Command, off_command: Command) -> None:
        """Set commands for a specific button slot."""
        self.on_commands[slot] = on_command
        self.off_commands[slot] = off_command
    
    def press_on_button(self, slot: int) -> None:
        """Press the ON button for a slot."""
        command = self.on_commands.get(slot)
        if command:
            command.execute()
            self.undo_command = command
    
    def press_off_button(self, slot: int) -> None:
        """Press the OFF button for a slot."""
        command = self.off_commands.get(slot)
        if command:
            command.execute()
            self.undo_command = command
    
    def press_undo_button(self) -> None:
        """Press the undo button."""
        if self.undo_command:
            self.undo_command.undo()
            self.undo_command = None


# Implementation 2: Command Pattern with Macro Commands

class MacroCommand(Command):
    """A command that executes multiple commands in sequence."""
    
    def __init__(self, commands: List[Command]):
        """Initialize with a list of commands."""
        self.commands = commands
    
    def execute(self) -> None:
        """Execute all commands in sequence."""
        for command in self.commands:
            command.execute()
    
    def undo(self) -> None:
        """Undo all commands in reverse order."""
        for command in reversed(self.commands):
            command.undo()


# Implementation 3: Function-Based Command Pattern

class FunctionalCommand:
    """Command implementation using functions."""
    
    def __init__(self, execute_func, undo_func):
        """Initialize with execute and undo functions."""
        self.execute_func = execute_func
        self.undo_func = undo_func
    
    def execute(self):
        """Execute the command."""
        return self.execute_func()
    
    def undo(self):
        """Undo the command."""
        return self.undo_func()


def create_light_on_command(light):
    """Create a command to turn on a light."""
    return FunctionalCommand(
        execute_func=lambda: light.turn_on(),
        undo_func=lambda: light.turn_off()
    )


def create_light_off_command(light):
    """Create a command to turn off a light."""
    return FunctionalCommand(
        execute_func=lambda: light.turn_off(),
        undo_func=lambda: light.turn_on()
    )


# Implementation 4: Command Pattern with History and Logging

class CommandHistory:
    """Keeps track of command execution for history and undo operations."""
    
    def __init__(self):
        """Initialize with empty history."""
        self.history: List[Command] = []
    
    def add(self, command: Command) -> None:
        """Add a command to history after execution."""
        self.history.append(command)
    
    def undo_last(self) -> None:
        """Undo the last command."""
        if self.history:
            command = self.history.pop()
            command.undo()


class LoggingCommand(Command):
    """A command decorator that adds logging."""
    
    def __init__(self, command: Command, logger):
        """Initialize with a command and logger."""
        self.command = command
        self.logger = logger
    
    def execute(self) -> None:
        """Log and execute the command."""
        self.logger.log(f"Executing {self.command.__class__.__name__}")
        self.command.execute()
    
    def undo(self) -> None:
        """Log and undo the command."""
        self.logger.log(f"Undoing {self.command.__class__.__name__}")
        self.command.undo()


class Logger:
    """Simple logger for command operations."""
    
    def log(self, message: str) -> None:
        """Log a message."""
        print(f"LOG: {message}")


# Usage Example
if __name__ == "__main__":
    # Example 1: Simple Command Pattern
    light = Light("Living Room")
    light_on = LightOnCommand(light)
    light_off = LightOffCommand(light)
    
    remote = RemoteControl()
    remote.set_command(0, light_on, light_off)
    
    remote.press_on_button(0)
    remote.press_off_button(0)
    remote.press_on_button(0)
    remote.press_undo_button()
    
    print("-" * 50)
    
    # Example 2: Macro Commands
    kitchen_light = Light("Kitchen")
    bedroom_light = Light("Bedroom")
    
    kitchen_on = LightOnCommand(kitchen_light)
    kitchen_off = LightOffCommand(kitchen_light)
    bedroom_on = LightOnCommand(bedroom_light)
    bedroom_off = LightOffCommand(bedroom_light)
    
    all_lights_on = MacroCommand([kitchen_on, bedroom_on])
    all_lights_off = MacroCommand([kitchen_off, bedroom_off])
    
    remote.set_command(1, all_lights_on, all_lights_off)
    
    remote.press_on_button(1)
    remote.press_off_button(1)
    
    print("-" * 50)
    
    # Example 3: Function-Based Commands
    office_light = Light("Office")
    
    office_on_cmd = create_light_on_command(office_light)
    office_off_cmd = create_light_off_command(office_light)
    
    remote.set_command(2, office_on_cmd, office_off_cmd)
    
    remote.press_on_button(2)
    remote.press_off_button(2)
    
    print("-" * 50)
    
    # Example 4: Commands with History and Logging
    hallway_light = Light("Hallway")
    logger = Logger()
    
    hallway_on = LightOnCommand(hallway_light)
    hallway_off = LightOffCommand(hallway_light)
    
    logging_on = LoggingCommand(hallway_on, logger)
    logging_off = LoggingCommand(hallway_off, logger)
    
    history = CommandHistory()
    
    logging_on.execute()
    history.add(logging_on)
    
    logging_off.execute()
    history.add(logging_off)
    
    history.undo_last()  # Undo turn off
    history.undo_last()  # Undo turn on