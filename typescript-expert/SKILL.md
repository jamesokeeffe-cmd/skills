---
name: typescript-expert
description: Production-grade TypeScript development expert with emphasis on type safety and modern patterns. Use when writing TypeScript code, designing type-safe APIs, implementing advanced type patterns (generics, utility types), configuring tsconfig, or migrating JavaScript to TypeScript. Activates for requests involving TypeScript, type inference, discriminated unions, branded types, or TypeScript compiler issues.
---

# TypeScript Expert

Adopt the perspective of a senior TypeScript developer with deep expertise in the type system and ecosystem.

## Core Expertise

- **Type System**: Generics, conditional types, mapped types, template literals
- **Advanced Patterns**: Discriminated unions, branded types, type guards
- **Configuration**: tsconfig optimization, strict mode, module resolution
- **Ecosystem**: tsx, tsc, ts-node, Vitest, type-only imports
- **Integration**: React types, Node types, library type definitions

## Type-First Development

### Start with Types
```typescript
// Define the shape before implementation
interface User {
  id: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  createdAt: Date;
}

interface UserService {
  findById(id: string): Promise<User | null>;
  create(data: CreateUserDTO): Promise<User>;
  updateRole(id: string, role: User['role']): Promise<void>;
}
```

### Utility Types Mastery
```typescript
// Extract and manipulate types
type CreateUserDTO = Omit<User, 'id' | 'createdAt'>;
type UserUpdate = Partial<Pick<User, 'email' | 'role'>>;
type UserKeys = keyof User; // 'id' | 'email' | 'role' | 'createdAt'

// Conditional types
type AsyncReturnType<T> = T extends (...args: any[]) => Promise<infer R> ? R : never;
```

## Advanced Patterns

### Discriminated Unions
```typescript
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };

function handleResult<T>(result: Result<T>) {
  if (result.success) {
    // TypeScript knows: result.data exists
    console.log(result.data);
  } else {
    // TypeScript knows: result.error exists
    console.error(result.error);
  }
}
```

### Branded Types
```typescript
// Prevent mixing IDs of different entities
type UserId = string & { readonly __brand: 'UserId' };
type OrderId = string & { readonly __brand: 'OrderId' };

function createUserId(id: string): UserId {
  return id as UserId;
}

function getUser(id: UserId): User { ... }
function getOrder(id: OrderId): Order { ... }

// Compile error: can't pass OrderId where UserId expected
getUser(orderId); // ❌ Error
```

### Type Guards
```typescript
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'email' in value
  );
}

// After type guard, TypeScript narrows the type
if (isUser(data)) {
  console.log(data.email); // ✓ TypeScript knows it's User
}
```

### Builder Pattern with Types
```typescript
class QueryBuilder<T extends object> {
  private query: Partial<T> = {};
  
  where<K extends keyof T>(key: K, value: T[K]): this {
    this.query[key] = value;
    return this;
  }
  
  build(): Partial<T> {
    return { ...this.query };
  }
}

// Type-safe: only allows valid User properties
new QueryBuilder<User>()
  .where('email', 'test@example.com')
  .where('role', 'admin')
  .build();
```

## Strict Configuration
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

## Common Pitfalls

- **any escape hatch**: Use `unknown` + type guards instead
- **Type assertions**: Prefer type guards over `as` casts
- **Missing null checks**: Enable `strictNullChecks`
- **Index signature abuse**: Use `Record<K, V>` or Maps
- **Over-typing**: Let inference work where it can

## Response Patterns

When writing TypeScript:
1. Define types/interfaces first
2. Use strict compiler options
3. Prefer type inference where unambiguous
4. Use discriminated unions for state
5. Add JSDoc for public APIs

When reviewing TypeScript:
1. Check for `any` usage (suggest alternatives)
2. Verify null handling
3. Look for unnecessary type assertions
4. Assess type complexity (simplify if needed)
5. Validate generic constraints
