As [1] covers the other identified patterns, this file maps the project patterns to the patterns proposed in [1].

Notes:
- The mapping expressions below are preserved as provided.
- This document focuses on readability and quick lookup.

## Order Patterns

| Pattern | Mapping |
| --- | --- |
| Precedes(a,b) | precedence(a,b) |
| ChainPrecedes(a,b,c) | precedence(a,b) and precedence(b,c) \|\| precedence(a,b,c) |
| LeadsTo(a,b) | response(a,b) |
| ChainLeadsTo(a,b,c) | response(a,b), and response(b,c) \|\| response(a,b,c) |
| DirectlyFollowedBy(a,b) | direct\_response(a,b) |
| Frees(a,b) | response(a,b) |
| Else | else |
| ElseNext | else |

## Occurrence Pattern

| Pattern | Mapping | Comment |
| --- | --- | --- |
| isAbsent | not occurrence(a) |  |
| isUniversal | occurrence(a) | Default scoping is the entire model. |
| existsoften | occurrence(M',a) and occurrence(M'', a) | Can also be done with iteration. |
| boundedexists | occurrence(M',a) | Scoping can be adapted by restricting the rule to a subprocess. |

## Composite Pattern

These patterns can be composed with ASTs. In this file, occurrence-based patterns are shown, but other pattern families can also be used as predicates.

| Pattern | Mapping |
| --- | --- |
| CoExists | not occurrence(a) or occurrence(b) |
| CoAbsent | occurrence(a) or not occurrence(b) |
| exclusive | not (occurence(A) and occurence(b)) | Pay attention to perspective here, at design time this means something else than intended|
| substitute | occurrence(a) or occurrence(b) |
| corequisite | precedence(a,b) or parallel(a,b) |
| mutex | exclusive(a,b) |

## Resource Pattern

This mapping does not distinguish resources from related concepts (for example roles or organizations); these can be incorporated in the same style.

| Pattern | Mapping | Comment |
| --- | --- | --- |
| PerformedBy(a,r) | r in resources(a) |  |
| segregatedFrom(a,b) | for r in resources(a): if r in resources(b): return false | If a 1:1 mapping between resources and activities is assumed, this becomes resources(a) != resources(b). |

All other patterns can also be composed accordinglly. Other Composition example:
- resources(a) != resources(b) == resources(c)

## Timed Pattern

| Pattern | Mapping | Comment |
| --- | --- | --- |
| MinDur(a,t) | min\_time\_between(a.start(), a.end(), t) |  |
| MaxDur(a,t) | max\_time\_between(a.start(), a.end(), t) |  |
| ExactDur(a,t) | MinDur(a,t) and MaxDur(a, t) | Practically impossible |
| Every | recurring |  |
| Within(a,b,t) | max\_time\_between(a,b,t) |  |
| AtLeastAfter(a,b,t) | min\_time\_between(a,b,t) |  |
| ExactlyAt(a,t) | exactly\_at(a, t) |  |
| ExactlyAfter | max\_time\_between(a,b,t) and min\_time\_between(a,b,t) | Practically impossible |

[1] Elgammal, A., Turetken, O. (2022). CRL and the Design-Time Compliance Management Framework. In: Polyvyanyy, A. (eds) Process Querying Methods. Springer, Cham. [doi](https://doi.org/10.1007/978-3-030-92875-9_10)
