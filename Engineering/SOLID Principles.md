# SOLID Principles

Five design principles for object-oriented programming that promote extensible, maintainable code.

## Why it matters

Without guiding principles, OOP code drifts toward classes that do too many things, resist change, and break in unexpected places when extended. SOLID provides a vocabulary and a set of rules for structuring code so that changes are local, extensions don't break existing behavior, and each piece has a clear purpose.

## How it works

### S — Single Responsibility Principle (SRP)

A class should do one thing. All its attributes and methods should relate to that one responsibility.

❌ A `Person` class that validates phone number formats — validation is the responsibility of the phone number, not the person.

✅ Extract `PhoneNumber` with its own validation. `Person` holds an instance of `PhoneNumber`.

Rule: if you can describe a class's purpose with "and," it probably has too many responsibilities.

---

### O — Open/Closed Principle (OCP)

Classes should be **open for extension, closed for modification**. Change behavior by subclassing, not by editing the original class.

❌ Fixing a `PhoneNumber` regex by editing the base class — this could break callers that relied on the old behavior.

✅ Extend `PhoneNumber` into `ReliablePhoneNumber` with the improved regex. Old callers are unaffected; new callers opt in.

Rule: source changes apply to all instances everywhere; inheritance changes apply only where explicitly adopted.

---

### L — Liskov Substitution Principle (LSP)

If `S` is a subtype of `T`, then anywhere `T` is used, `S` can be substituted without breaking correctness.

`ReliablePhoneNumber` extends `PhoneNumber`, so anywhere code accepts a `PhoneNumber`, a `ReliablePhoneNumber` works. Substituting it doesn't break the contract — it just validates more strictly.

Rule: subtypes must honor the behavioral contract of the parent, not just the interface.

---

### I — Interface Segregation Principle (ISP)

Don't force classes to implement interfaces they don't use. Break large interfaces into smaller, focused ones.

❌ A single `WorkerInf` interface with `doNLP`, `doDeployment`, `knowsBlockchain`, `canKubernetes` — a `SoftwareEngineer` shouldn't be required to implement `doNLP`.

✅ Separate `DataScientistInf` and `SoftwareEngineerInf`. Each class implements only what's relevant.

Rule: clients should not be forced to depend on methods they do not use.

---

### D — Dependency Inversion Principle (DIP)

High-level modules should not depend on low-level implementation details. Both should depend on abstractions. Layers should interact through interfaces, not concrete implementations.

❌ A `ProjectManager` that directly calls `addIndex()`, `makeJoin()`, `addComponent()` etc. — it's entangled in the details of every layer.

✅ `ProjectManager` delegates to `DatabaseTaskLead`, `FrontendTaskLead`, `BackendTaskLead` — each a black box. `ProjectManager` orchestrates, not implements.

Rule: orchestrators should depend on abstractions; specialists implement them.

---

### Summary

| Principle | In one line |
|---|---|
| SRP | One class, one job |
| OCP | Extend, don't edit |
| LSP | Subtypes must honor the parent contract |
| ISP | Small, focused interfaces over large ones |
| DIP | Depend on abstractions, not implementations |

## Key tradeoffs

- **SRP vs. over-fragmentation** — taken too far, SRP produces dozens of tiny classes that are individually simple but hard to navigate; judgment required
- **OCP vs. initial design cost** — designing for extension up front adds complexity; premature extensibility is its own problem
- **LSP and behavioral contracts** — interfaces enforce method signatures, not behavioral semantics; LSP violations often compile and test correctly, only revealing problems at runtime
- **ISP vs. proliferation** — too many tiny interfaces can make dependency graphs hard to follow; balance specificity with navigability
- **DIP and abstraction layers** — indirection adds cognitive overhead; DIP is most valuable at architectural seams, not everywhere

