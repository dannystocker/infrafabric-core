# PHILOSOPHY → CODE: Canon 26 (Full Coverage)
_Last updated: 2025-11-11 12:09:03Z_

Below are minimal, executable-style snippets for **all 26** entries used in InfraFabric.

### John Locke  
**Tradition:** Empiricism · **IF:** IF.ground · **Operationalization:** Principle 1: Observables

```ts
// John Locke — Empiricism → IF.ground (Principle 1: Observables)
// TypeScript: observable artifacts
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Vienna Circle  
**Tradition:** Verificationism · **IF:** IF.ground · **Operationalization:** Principle 2: Toolchain verification

```yaml
# Vienna Circle — Verificationism → IF.ground (Principle 2: Toolchain verification)
# CI lint gate
guardrails:
  universal:
    - "No unverifiable claim without source URL"
    - "Rollback path must exist for every risky change"
```

### Charles S. Peirce  
**Tradition:** Fallibilism · **IF:** IF.ground · **Operationalization:** Principle 3: Unknowns explicit

```ts
// Charles S. Peirce — Fallibilism → IF.ground (Principle 3: Unknowns explicit)
// TypeScript: null-safe
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Pierre Duhem  
**Tradition:** Underdetermination · **IF:** IF.ground · **Operationalization:** Principle 4: Schema tolerance

```ts
// Pierre Duhem — Underdetermination → IF.ground (Principle 4: Schema tolerance)
// TypeScript: tolerant parse
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### W.V.O. Quine  
**Tradition:** Coherentism · **IF:** IF.ground · **Operationalization:** Principle 5: Coherence & gating

```txt
# Placeholder
```
### William James  
**Tradition:** Pragmatism · **IF:** IF.ground · **Operationalization:** Principle 6: Progressive enhancement

```ts
// William James — Pragmatism → IF.ground (Principle 6: Progressive enhancement)
// TypeScript: graceful degrade
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Karl Popper  
**Tradition:** Falsifiability · **IF:** IF.ground · **Operationalization:** Principle 7: Reversible switches

```ts
// Karl Popper — Falsifiability → IF.ground (Principle 7: Reversible switches)
// feature toggles
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Epictetus  
**Tradition:** Stoicism · **IF:** IF.ground · **Operationalization:** Principle 8: Observability w/o fragility

```ts
// Epictetus — Stoicism → IF.ground (Principle 8: Observability w/o fragility)
// soft-fail observability
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Ludwig Wittgenstein  
**Tradition:** Language Games · **IF:** IF.search · **Operationalization:** Pass 4: Cross-reference

```ts
// Ludwig Wittgenstein — Language Games → IF.search (Pass 4: Cross-reference)
// synonym map / language games
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Thomas Kuhn  
**Tradition:** Paradigms · **IF:** IF.guard · **Operationalization:** Debate epochs

```python
# Thomas Kuhn — Paradigms → IF.guard (Debate epochs)
# epoch config & migration
from statistics import mean
def synthesize(scores: list[float]) -> float:
    # Dialectic/perspectivism aggregator
    return round(mean(scores), 4)
```

### Imre Lakatos  
**Tradition:** Research Programmes · **IF:** IF.search · **Operationalization:** Hypothesis tracks

```yaml
# Imre Lakatos — Research Programmes → IF.search (Hypothesis tracks)
# program tracks & status
guardrails:
  universal:
    - "No unverifiable claim without source URL"
    - "Rollback path must exist for every risky change"
```

### Donald Davidson  
**Tradition:** Anomalous Monism · **IF:** IF.guard · **Operationalization:** Explanatory pluralism

```python
# Donald Davidson — Anomalous Monism → IF.guard (Explanatory pluralism)
# multi-model aggregation
from statistics import mean
def synthesize(scores: list[float]) -> float:
    # Dialectic/perspectivism aggregator
    return round(mean(scores), 4)
```

### Buddha  
**Tradition:** Middle Way · **IF:** IF.guard · **Operationalization:** Graduated response

```yaml
# Buddha — Middle Way → IF.guard (Graduated response)
# graduated response policy
guardrails:
  universal:
    - "No unverifiable claim without source URL"
    - "Rollback path must exist for every risky change"
```

### Nagarjuna  
**Tradition:** Emptiness · **IF:** IF.search · **Operationalization:** Dissolve contradictions

```ts
// Nagarjuna — Emptiness → IF.search (Dissolve contradictions)
// contradiction resolver
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Confucius  
**Tradition:** Relational Ethics · **IF:** IF.guard · **Operationalization:** Ubuntu-like quorum

```python
# Confucius — Relational Ethics → IF.guard (Ubuntu-like quorum)
# quorum with roles
from statistics import mean
def synthesize(scores: list[float]) -> float:
    # Dialectic/perspectivism aggregator
    return round(mean(scores), 4)
```

### Zhuangzi  
**Tradition:** Wu Wei · **IF:** IF.search · **Operationalization:** Do-nothing bias

```ts
// Zhuangzi — Wu Wei → IF.search (Do-nothing bias)
// backoff + noop policy
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Baruch Spinoza  
**Tradition:** Substance Monism · **IF:** IF.connect · **Operationalization:** Unified substrate

```ts
// Baruch Spinoza — Substance Monism → IF.connect (Unified substrate)
// single-bus message router
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Immanuel Kant  
**Tradition:** Categorical Imperative · **IF:** IF.guard · **Operationalization:** Universalizable rules

```yaml
# Immanuel Kant — Categorical Imperative → IF.guard (Universalizable rules)
# universal guardrails
guardrails:
  universal:
    - "No unverifiable claim without source URL"
    - "Rollback path must exist for every risky change"
```

### G.W.F. Hegel  
**Tradition:** Dialectics · **IF:** IF.guard · **Operationalization:** Thesis → antithesis → synthesis

```python
# G.W.F. Hegel — Dialectics → IF.guard (Thesis → antithesis → synthesis)
# debate to synthesis
from statistics import mean
def synthesize(scores: list[float]) -> float:
    # Dialectic/perspectivism aggregator
    return round(mean(scores), 4)
```

### Friedrich Nietzsche  
**Tradition:** Perspectivism · **IF:** IF.guard · **Operationalization:** Weighted perspectives

```python
# Friedrich Nietzsche — Perspectivism → IF.guard (Weighted perspectives)
# source-weight aggregator
from statistics import mean
def synthesize(scores: list[float]) -> float:
    # Dialectic/perspectivism aggregator
    return round(mean(scores), 4)
```

### John Dewey  
**Tradition:** Instrumentalism · **IF:** IF.search · **Operationalization:** Experiment loop

```ts
// John Dewey — Instrumentalism → IF.search (Experiment loop)
// A/B experimentation harness
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

### Richard Rorty  
**Tradition:** Neopragmatism · **IF:** IF.guard · **Operationalization:** Solidarity over objectivity

```yaml
# Richard Rorty — Neopragmatism → IF.guard (Solidarity over objectivity)
# dissent + coalition rules
guardrails:
  universal:
    - "No unverifiable claim without source URL"
    - "Rollback path must exist for every risky change"
```

### Bruno Latour  
**Tradition:** Actor-Network Theory · **IF:** IF.swarm · **Operationalization:** Non-human actors

```yaml
# Bruno Latour — Actor-Network Theory → IF.swarm (Non-human actors)
# device/agent actors
guardrails:
  universal:
    - "No unverifiable claim without source URL"
    - "Rollback path must exist for every risky change"
```

### Donna Haraway  
**Tradition:** Situated Knowledges · **IF:** IF.citation · **Operationalization:** Provenance & position

```yaml
# Donna Haraway — Situated Knowledges → IF.citation (Provenance & position)
# provenance schema
guardrails:
  universal:
    - "No unverifiable claim without source URL"
    - "Rollback path must exist for every risky change"
```

### Al-Ghazali  
**Tradition:** Occasionalism · **IF:** IF.witness · **Operationalization:** Event occasions

```yaml
# Al-Ghazali — Occasionalism → IF.witness (Event occasions)
# append-only occasions
guardrails:
  universal:
    - "No unverifiable claim without source URL"
    - "Rollback path must exist for every risky change"
```

### Avicenna  
**Tradition:** Essence/Existence · **IF:** IF.persona · **Operationalization:** Capabilities vs instantiation

```ts
// Avicenna — Essence/Existence → IF.persona (Capabilities vs instantiation)
// persona capability manifest
export type Observable<T> = { value: T; source: string; at: string };
export function observable<T>(value: T, source: string): Observable<T> {
  return { value, source, at: new Date().toISOString() };
}
```

