/**
 * Sample implementations of the Command pattern in JavaScript.
 * 
 * The Command pattern encapsulates a request as an object, allowing users to
 * parameterize clients with different requests, queue or log requests, and
 * support undoable operations.
 */

// Implementation 1: Classic Command Pattern

/**
 * Command interface (abstract class in JavaScript)
 */
class Command {
  execute() {
    throw new Error('Command.execute() must be implemented');
  }
  
  undo() {
    throw new Error('Command.undo() must be implemented');
  }
}

/**
 * Concrete command for turning on a light
 */
class LightOnCommand extends Command {
  constructor(light) {
    super();
    this.light = light;
  }
  
  execute() {
    this.light.turnOn();
  }
  
  undo() {
    this.light.turnOff();
  }
}

/**
 * Concrete command for turning off a light
 */
class LightOffCommand extends Command {
  constructor(light) {
    super();
    this.light = light;
  }
  
  execute() {
    this.light.turnOff();
  }
  
  undo() {
    this.light.turnOn();
  }
}

/**
 * Receiver class that performs the actual actions
 */
class Light {
  constructor(name) {
    this.name = name;
    this.isOn = false;
  }
  
  turnOn() {
    this.isOn = true;
    console.log(`${this.name} light is now ON`);
  }
  
  turnOff() {
    this.isOn = false;
    console.log(`${this.name} light is now OFF`);
  }
}

/**
 * Invoker class that asks the command to carry out the request
 */
class RemoteControl {
  constructor() {
    this.onCommands = {};
    this.offCommands = {};
    this.undoCommand = null;
  }
  
  setCommand(slot, onCommand, offCommand) {
    this.onCommands[slot] = onCommand;
    this.offCommands[slot] = offCommand;
  }
  
  pressOnButton(slot) {
    const command = this.onCommands[slot];
    if (command) {
      command.execute();
      this.undoCommand = command;
    }
  }
  
  pressOffButton(slot) {
    const command = this.offCommands[slot];
    if (command) {
      command.execute();
      this.undoCommand = command;
    }
  }
  
  pressUndoButton() {
    if (this.undoCommand) {
      this.undoCommand.undo();
      this.undoCommand = null;
    }
  }
}

// Implementation 2: Command Pattern with Macro Commands

/**
 * A command that executes multiple commands in sequence
 */
class MacroCommand extends Command {
  constructor(commands) {
    super();
    this.commands = commands;
  }
  
  execute() {
    for (const command of this.commands) {
      command.execute();
    }
  }
  
  undo() {
    // Undo commands in reverse order
    for (let i = this.commands.length - 1; i >= 0; i--) {
      this.commands[i].undo();
    }
  }
}

// Implementation 3: Function-Based Command Pattern

/**
 * Command implementation using functions
 */
class FunctionalCommand {
  constructor(executeFunc, undoFunc) {
    this.executeFunc = executeFunc;
    this.undoFunc = undoFunc;
  }
  
  execute() {
    return this.executeFunc();
  }
  
  undo() {
    return this.undoFunc();
  }
}

/**
 * Create a command to turn on a light
 */
function createLightOnCommand(light) {
  return new FunctionalCommand(
    () => light.turnOn(),
    () => light.turnOff()
  );
}

/**
 * Create a command to turn off a light
 */
function createLightOffCommand(light) {
  return new FunctionalCommand(
    () => light.turnOff(),
    () => light.turnOn()
  );
}

// Implementation 4: Command Pattern with Queue and History

/**
 * Keeps track of command execution for history and undo operations
 */
class CommandHistory {
  constructor() {
    this.history = [];
  }
  
  add(command) {
    this.history.push(command);
  }
  
  undoLast() {
    if (this.history.length > 0) {
      const command = this.history.pop();
      command.undo();
    }
  }
}

/**
 * A command decorator that adds logging
 */
class LoggingCommand {
  constructor(command, logger) {
    this.command = command;
    this.logger = logger;
  }
  
  execute() {
    this.logger.log(`Executing ${this.command.constructor.name}`);
    this.command.execute();
  }
  
  undo() {
    this.logger.log(`Undoing ${this.command.constructor.name}`);
    this.command.undo();
  }
}

/**
 * Simple logger for command operations
 */
class Logger {
  log(message) {
    console.log(`LOG: ${message}`);
  }
}

// Implementation 5: Command Pattern using Object Composition

/**
 * Command Factory - implements the command pattern with object composition
 */
class CommandFactory {
  static createCommand(receiver, action, undoAction) {
    return {
      execute: () => receiver[action](),
      undo: () => receiver[undoAction]()
    };
  }
}

// Usage examples
function runExamples() {
  // Example 1: Simple Command Pattern
  console.log("Example 1: Simple Command Pattern");
  
  const light = new Light("Living Room");
  const lightOn = new LightOnCommand(light);
  const lightOff = new LightOffCommand(light);
  
  const remote = new RemoteControl();
  remote.setCommand(0, lightOn, lightOff);
  
  remote.pressOnButton(0);
  remote.pressOffButton(0);
  remote.pressOnButton(0);
  remote.pressUndoButton();
  
  console.log("-".repeat(50));
  
  // Example 2: Macro Commands
  console.log("Example 2: Macro Commands");
  
  const kitchenLight = new Light("Kitchen");
  const bedroomLight = new Light("Bedroom");
  
  const kitchenOn = new LightOnCommand(kitchenLight);
  const kitchenOff = new LightOffCommand(kitchenLight);
  const bedroomOn = new LightOnCommand(bedroomLight);
  const bedroomOff = new LightOffCommand(bedroomLight);
  
  const allLightsOn = new MacroCommand([kitchenOn, bedroomOn]);
  const allLightsOff = new MacroCommand([kitchenOff, bedroomOff]);
  
  remote.setCommand(1, allLightsOn, allLightsOff);
  
  remote.pressOnButton(1);
  remote.pressOffButton(1);
  
  console.log("-".repeat(50));
  
  // Example 3: Function-Based Commands
  console.log("Example 3: Function-Based Commands");
  
  const officeLight = new Light("Office");
  
  const officeOnCmd = createLightOnCommand(officeLight);
  const officeOffCmd = createLightOffCommand(officeLight);
  
  remote.setCommand(2, officeOnCmd, officeOffCmd);
  
  remote.pressOnButton(2);
  remote.pressOffButton(2);
  
  console.log("-".repeat(50));
  
  // Example 4: Commands with History and Logging
  console.log("Example 4: Commands with History and Logging");
  
  const hallwayLight = new Light("Hallway");
  const logger = new Logger();
  
  const hallwayOn = new LightOnCommand(hallwayLight);
  const hallwayOff = new LightOffCommand(hallwayLight);
  
  const loggingOn = new LoggingCommand(hallwayOn, logger);
  const loggingOff = new LoggingCommand(hallwayOff, logger);
  
  const history = new CommandHistory();
  
  loggingOn.execute();
  history.add(loggingOn);
  
  loggingOff.execute();
  history.add(loggingOff);
  
  history.undoLast(); // Undo turn off
  history.undoLast(); // Undo turn on
  
  console.log("-".repeat(50));
  
  // Example 5: Object Composition
  console.log("Example 5: Object Composition");
  
  const garageLight = new Light("Garage");
  
  const garageLightOn = CommandFactory.createCommand(garageLight, 'turnOn', 'turnOff');
  const garageLightOff = CommandFactory.createCommand(garageLight, 'turnOff', 'turnOn');
  
  garageLightOn.execute();
  garageLightOff.execute();
  garageLightOff.undo();
}

// Uncomment to run the examples
// runExamples();