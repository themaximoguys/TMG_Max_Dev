# Maximo Workflow Expression Syntax Reference

Complete reference for SQL WHERE clause expressions used in Condition nodes and connection line conditions.

---

## Bind Variable Types

### 1. Field References (`:FIELDNAME`)

Direct reference to an attribute on the controlled record (the MBO the workflow is assigned to).

```sql
:STATUS = 'APPR'
:TOTALCOST > 5000
:WOPRIORITY < 3
:SITEID = 'BEDFORD'
:WORKTYPE = 'PM'
:OWNER IS NOT NULL
```

**Rules:**
- Always UPPERCASE for field names
- String values in single quotes
- Numeric values without quotes
- NULL checks: `IS NULL` / `IS NOT NULL`

### 2. System Variables (`:&variable&`)

Runtime system values enclosed in `&` delimiters.

| Variable | Description | Example |
|----------|-------------|---------|
| `:&user&` | Logged-in user ID | `:CHANGEBY = :&user&` |
| `:&personid&` | Person ID of logged-in user | `:SUPERVISOR = :&personid&` |
| `:&date&` | Current date | `:TARGCOMPDATE < :&date&` |
| `:&datetime&` | Current date and time | `:REPORTDATE <= :&datetime&` |
| `:&appname&` | Current application name | `:&appname& = 'WOTRACK'` |
| `:&mboname&` | Current MBO name | `:&mboname& = 'WORKORDER'` |
| `:&ownername&` | Owner MBO name | — |

### 3. Old Value References (`:$old_FIELDNAME`)

The original database value BEFORE the current change. Useful for detecting field changes.

```sql
:STATUS != :$old_STATUS
:$old_STATUS = 'WAPPR' AND :STATUS = 'APPR'
:TOTALCOST > :$old_TOTALCOST
```

### 4. Related Object References (`:RELATIONSHIP.FIELDNAME`)

Access fields on related MBOs through defined Maximo relationships.

```sql
:ASSET.ASSETTYPE = 'IT'
:ASSET.STATUS = 'OPERATING'
:LOCATION.TYPE = 'STOREROOM'
:PO.POLINE.RECEIVEDQTY = 0
:&owner&.DESCRIPTION
```

**Rules:**
- Relationship names must be valid Maximo relationships on the object
- Can chain through multiple relationships with dots
- Use `:&owner&.FIELD` to access the owner MBO's fields

---

## Operators

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equal | `:STATUS = 'APPR'` |
| `!=` | Not equal | `:WORKTYPE != 'PM'` |
| `<>` | Not equal (alternate) | `:PRIORITY <> 1` |
| `<` | Less than | `:WOPRIORITY < 3` |
| `>` | Greater than | `:TOTALCOST > 5000` |
| `<=` | Less than or equal | `:ESTDUR <= 8.0` |
| `>=` | Greater than or equal | `:TOTALCOST >= 1000` |

### Logical Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `AND` | Both conditions true | `:STATUS = 'APPR' AND :TOTALCOST > 1000` |
| `OR` | Either condition true | `:PRIORITY = 1 OR :PRIORITY = 2` |
| `NOT` | Negation | `NOT :STATUS = 'CAN'` |

**Precedence:** `NOT` > `AND` > `OR`. Use parentheses for clarity.

### NULL Checks

```sql
:OWNER IS NULL
:SUPERVISOR IS NOT NULL
:JPNUM IS NULL
```

### String Operations

| Operator | Description | Example |
|----------|-------------|---------|
| `LIKE` | Pattern matching | `:DESCRIPTION LIKE '%EMERGENCY%'` |
| `IN` | Set membership | `:STATUS IN ('WAPPR', 'APPR')` |
| `NOT IN` | Not in set | `:WORKTYPE NOT IN ('PM', 'CAL')` |

### Subselect (Advanced)

For complex queries that need to reference other tables:

```sql
EXISTS (SELECT 1 FROM workorder WHERE wonum = :WONUM AND siteid = :SITEID)

:TOTALCOST <= (
  SELECT MAX(lt.polimit)
  FROM groupuser gu
  LEFT JOIN limittolerance lt ON lt.groupname = gu.groupname AND lt.orgid = :ORGID
  WHERE gu.userid = :&user&
)
```

---

## Expression Examples by Use Case

### Approval Thresholds

```sql
-- Cost-based routing
:TOTALCOST > 5000
:TOTALCOST > 1000 AND :TOTALCOST <= 5000
:TOTALCOST <= 1000

-- Priority-based
:WOPRIORITY < 3
:WOPRIORITY = 1

-- Work type
:WORKTYPE = 'EM'
:WORKTYPE IN ('CM', 'EM')
```

### Status Checks

```sql
-- Current status
:STATUS = 'WAPPR'
:STATUS = 'APPR'
:STATUS IN ('WAPPR', 'INPRG')

-- Status changed
:STATUS != :$old_STATUS
:$old_STATUS = 'WAPPR' AND :STATUS = 'APPR'

-- Check if in approval state
:STATUS = 'WAPPR'
```

### User/Owner Checks

```sql
-- Is the logged-in user the owner?
:OWNER = :&user&
:OWNER = :&personid&

-- Is the logged-in user the supervisor?
:SUPERVISOR = :&personid&

-- Did the logged-in user report this?
:REPORTEDBY = :&personid&

-- Is there an owner assigned?
:OWNER IS NOT NULL
```

### Asset/Location Conditions

```sql
-- Asset type routing
:ASSET.ASSETTYPE = 'IT'
:ASSET.ASSETTYPE = 'FLEET'
:ASSET.PRIORITY = 1

-- Location type
:LOCATION.TYPE = 'OPERATING'

-- Classification-based
:CLASSSTRUCTUREID = 122
:ASSET.CLASSSTRUCTUREID = 1085
```

### Date/Time Conditions

```sql
-- Overdue
:TARGCOMPDATE < :&date&

-- Created today
:REPORTDATE >= :&date&

-- Scheduled for future
:TARGSTARTDATE > :&datetime&
```

### Site/Org Routing

```sql
-- Route by site
:SITEID = 'BEDFORD'
:SITEID IN ('BEDFORD', 'NASHUA')

-- Route by organization
:ORGID = 'EAGLENA'
```

### PO-Specific

```sql
-- PO type
:POTYPE = 'STD'

-- PO with specific vendor
:VENDOR = 'V001'

-- PO revision check
:REVISIONNUM > 1

-- Cost thresholds
:TOTALCOST > 10000
:TOTALCOST > 1000 AND :TOTALCOST <= 10000
```

### PR-Specific

```sql
-- PR requester
:REQUESTEDBY = :&personid&

-- PR cost
:TOTALCOST > 5000
```

### Service Request (PMCOMSR)

```sql
-- Priority routing
:REPORTEDPRIORITY = 1
:INTERNALPRIORITY <= 2

-- Owner assignment check
:OWNERGROUP IS NOT NULL
:OWNER IS NULL AND :OWNERGROUP IS NULL
```

### Invoice

```sql
-- Invoice amount
:TOTALCOST > 10000

-- Related PO check
:PONUM IS NOT NULL
```

---

## Common Mistakes to Avoid

| Mistake | Wrong | Correct |
|---------|-------|---------|
| Double quotes for strings | `:STATUS = "APPR"` | `:STATUS = 'APPR'` |
| Missing colon on field | `STATUS = 'APPR'` | `:STATUS = 'APPR'` |
| Wrong system var syntax | `:user` or `&user&` | `:&user&` |
| Wrong old value syntax | `:old_STATUS` or `$old_STATUS` | `:$old_STATUS` |
| Case sensitivity on values | `:STATUS = 'appr'` | `:STATUS = 'APPR'` (use internal value) |
| Spaces in bind variable | `: STATUS` | `:STATUS` |
| Using `==` instead of `=` | `:STATUS == 'APPR'` | `:STATUS = 'APPR'` |

---

## XML Escaping

When conditions appear in XML, these characters must be escaped:

| Character | XML Entity |
|-----------|-----------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| `"` | `&quot;` |
| `'` | `&apos;` (or use `&#39;`) |

Example in XML:
```xml
<CONDITION>:TOTALCOST &gt; 5000</CONDITION>
<CONDITION>:WOPRIORITY &lt; 3 AND :WORKTYPE = &apos;EM&apos;</CONDITION>
```
