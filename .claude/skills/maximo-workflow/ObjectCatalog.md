# Maximo Object Catalog for Workflow

Reference for all Maximo objects commonly used in workflows. Each entry includes key fields, statuses, common actions, and the typical application.

---

## WORKORDER (Work Order)

**Application:** WOTRACK (Work Order Tracking)
**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| WONUM | VARCHAR(20) | Work order number (unique per site) |
| DESCRIPTION | VARCHAR(100) | Work order description |
| STATUS | VARCHAR(16) | Current status (synonym domain: WOSTATUS) |
| WOPRIORITY | INT | Priority (1=highest) |
| TOTALCOST | DECIMAL | Total estimated cost |
| WORKTYPE | VARCHAR(5) | Work type (CM, PM, EM, etc.) |
| SITEID | VARCHAR(8) | Site identifier |
| ORGID | VARCHAR(8) | Organization identifier |
| OWNER | VARCHAR(30) | Owner person |
| OWNERGROUP | VARCHAR(8) | Owner person group |
| SUPERVISOR | VARCHAR(30) | Supervisor person |
| LEAD | VARCHAR(30) | Lead person |
| REPORTEDBY | VARCHAR(30) | Person who reported |
| REPORTDATE | DATETIME | Date reported |
| TARGSTARTDATE | DATETIME | Target start date |
| TARGCOMPDATE | DATETIME | Target completion date |
| JPNUM | VARCHAR(12) | Job plan number |
| LOCATION | VARCHAR(12) | Location |
| ASSETNUM | VARCHAR(12) | Asset number |
| GLACCOUNT | VARCHAR(30) | GL account |
| CLASSSTRUCTUREID | BIGINT | Classification |
| FAILURECODE | VARCHAR(8) | Failure code |
| PROBLEMCODE | VARCHAR(8) | Problem code |
| ESTDUR | DECIMAL | Estimated duration (hours) |

**Statuses (WOSTATUS domain):**

| Internal | Description | Typical Flow |
|----------|-------------|--------------|
| WAPPR | Waiting on Approval | Initial submission → approval required |
| APPR | Approved | Approved, ready for planning/scheduling |
| INPRG | In Progress | Work has started |
| COMP | Complete | Work finished |
| CLOSE | Closed | Financially closed |
| CAN | Cancelled | Cancelled |
| WMATL | Waiting on Material | Pending material availability |
| WSCH | Waiting to be Scheduled | Approved, awaiting scheduling |
| HISTEDIT | History Edit | Historical correction |

**Common Actions:** APPR (Approve), WAPPR (Set to Waiting Approval), INPRG (Start Work), COMP (Complete), CLOSE (Close), CAN (Cancel)

---

## WOACTIVITY (Work Order Activity/Task)

**Application:** WOTRACK
**Key Fields:** Same as WORKORDER (inherits), plus PARENT (parent WO number), TASKID (task sequence)
**Statuses:** Same as WORKORDER
**Notes:** Activities are child work orders. Workflow on WOACTIVITY controls task-level approval separate from the parent WO.

---

## PO (Purchase Order)

**Application:** PO (Purchase Orders)
**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| PONUM | VARCHAR(10) | PO number |
| DESCRIPTION | VARCHAR(100) | PO description |
| STATUS | VARCHAR(16) | Current status (POSTATUS) |
| TOTALCOST | DECIMAL | Total PO cost |
| POTYPE | VARCHAR(15) | PO type (STD, BLANKET, CONTRACT) |
| VENDOR | VARCHAR(12) | Vendor code |
| PURCHASEAGENT | VARCHAR(30) | Purchasing agent |
| ORGID | VARCHAR(8) | Organization |
| SITEID | VARCHAR(8) | Site |
| CURRENCYCODE | VARCHAR(3) | Currency |
| ORDERDATE | DATETIME | Order date |
| REVISIONNUM | INT | Revision number |
| CONTRACTREFNUM | VARCHAR(8) | Contract reference |

**Statuses (POSTATUS domain):**

| Internal | Description |
|----------|-------------|
| WAPPR | Waiting on Approval |
| APPR | Approved |
| CLOSE | Closed |
| CAN | Cancelled |
| PNDREV | Pending Revision |
| REVISE | In Revision |

**Common Actions:** APPR, WAPPR, CLOSE, CAN, PNDREV

---

## PR (Purchase Requisition)

**Application:** PR (Purchase Requisitions)
**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| PRNUM | VARCHAR(10) | PR number |
| DESCRIPTION | VARCHAR(100) | Description |
| STATUS | VARCHAR(16) | Status (PRSTATUS) |
| TOTALCOST | DECIMAL | Total cost |
| REQUESTEDBY | VARCHAR(30) | Requester |
| ORGID | VARCHAR(8) | Organization |
| SITEID | VARCHAR(8) | Site |

**Statuses:** WAPPR, APPR, CLOSE, CAN, PNDREV

---

## INVOICE

**Application:** IV (Invoices)
**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| INVOICENUM | VARCHAR(10) | Invoice number |
| DESCRIPTION | VARCHAR(100) | Description |
| STATUS | VARCHAR(16) | Status (INVOICESTATUS) |
| TOTALCOST | DECIMAL | Total amount |
| VENDOR | VARCHAR(12) | Vendor code |
| PONUM | VARCHAR(10) | Related PO |

**Statuses:** WAPPR, APPR, CLOSE, CAN, PAID

---

## ASSET

**Application:** ASSET (Assets)
**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| ASSETNUM | VARCHAR(12) | Asset number |
| DESCRIPTION | VARCHAR(100) | Description |
| STATUS | VARCHAR(16) | Status (ASSETSTATUS) |
| ASSETTYPE | VARCHAR(15) | Type (IT, FLEET, PRODUCTION, etc.) |
| LOCATION | VARCHAR(12) | Location |
| SERIALNUM | VARCHAR(64) | Serial number |
| SITEID | VARCHAR(8) | Site |
| PURCHASEPRICE | DECIMAL | Purchase price |
| REPLACECOST | DECIMAL | Replacement cost |
| PRIORITY | INT | Priority |
| CLASSSTRUCTUREID | BIGINT | Classification |

**Statuses:** NOT READY, OPERATING, ACTIVE, INACTIVE, DECOMMISSIONED, DISPOSED

---

## SR / PMCOMSR (Service Request)

**Application:** SR (Service Requests)
**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| TICKETID | VARCHAR(10) | Ticket ID (SR number) |
| DESCRIPTION | VARCHAR(100) | Description |
| STATUS | VARCHAR(16) | Status (SRSTATUS) |
| REPORTEDPRIORITY | INT | Reported priority |
| INTERNALPRIORITY | INT | Internal priority |
| REPORTEDBY | VARCHAR(30) | Reporter |
| OWNER | VARCHAR(30) | Owner |
| OWNERGROUP | VARCHAR(8) | Owner group |
| CLASSSTRUCTUREID | BIGINT | Classification |
| SITEID | VARCHAR(8) | Site |

**Statuses:** NEW, QUEUED, INPROG, PENDING, RESOLVED, CLOSED, CAN

**Notes:** The ISM* workflows (ISMSUBMIT, ISMACCEPT, ISMREJECT, ISMCANCEL, ISMCLOSE, ISMREPLACE) control the full SR lifecycle. Object name in workflow is **PMCOMSR** (not SR).

---

## ITEM

**Application:** ITEM (Item Master)
**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| ITEMNUM | VARCHAR(30) | Item number |
| DESCRIPTION | VARCHAR(100) | Description |
| STATUS | VARCHAR(16) | Status |
| ITEMTYPE | VARCHAR(15) | Type (ITEM, TOOL, MATERIAL) |
| ORDERUNIT | VARCHAR(16) | Order unit |
| ISSUEUNIT | VARCHAR(16) | Issue unit |

**Statuses:** PLANNING, ACTIVE, PENDING OBSOLESCENCE, OBSOLETE

---

## MAXUSER (User Record)

**Application:** MAXUSER (Users)
**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| USERID | VARCHAR(30) | User ID |
| STATUS | VARCHAR(12) | Status |
| PERSONID | VARCHAR(30) | Associated person |
| DEFSITE | VARCHAR(8) | Default site |

**Statuses:** ACTIVE, INACTIVE, BLOCKED, NEWREG

**Notes:** LDAPUSERWF and SELFREG workflows control user approval.

---

## INBOUNDCOMM (Inbound Communication)

**Application:** Email Listener processing
**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| INBOUNDCOMMID | BIGINT | Unique ID |
| MSGSUBJECT | VARCHAR(300) | Email subject |
| MSGBODY | CLOB | Email body |
| FROMADDRESS | VARCHAR(200) | Sender email |
| STATUS | VARCHAR(16) | Processing status |

**Notes:** MFMAILRCV, LSNRBP, and IBEP workflows process incoming emails.

---

## LOCATIONS

**Application:** LOCATION (Locations)
**Key Fields:** LOCATION, DESCRIPTION, STATUS, TYPE, SITEID
**Statuses:** OPERATING, ACTIVE, INACTIVE, DECOMMISSIONED

---

## JOBPLAN

**Application:** JOBPLAN (Job Plans)
**Key Fields:** JPNUM, DESCRIPTION, STATUS, SITEID, ORGID
**Statuses:** DRAFT, ACTIVE, INACTIVE, REVISED
**Notes:** JPACTIVATE workflow handles activation approval.

---

## Quick Object Lookup

| Object | Application | Primary Key Field | Status Domain | Common Workflow |
|--------|-------------|-------------------|---------------|-----------------|
| WORKORDER | WOTRACK | WONUM | WOSTATUS | WOAPPR |
| WOACTIVITY | WOTRACK | WONUM+TASKID | WOSTATUS | APPWFWOA |
| PO | PO | PONUM | POSTATUS | POAPPR |
| PR | PR | PRNUM | PRSTATUS | PRAPPR |
| INVOICE | IV | INVOICENUM | INVOICESTATUS | INVAPPR |
| ASSET | ASSET | ASSETNUM | ASSETSTATUS | ASSETAPPR |
| PMCOMSR | SR | TICKETID | SRSTATUS | ISM* series |
| ITEM | ITEM | ITEMNUM | ITEMSTATUS | ITEMADD |
| MAXUSER | MAXUSER | USERID | — | LDAPUSERWF, SELFREG |
| INBOUNDCOMM | — | INBOUNDCOMMID | — | MFMAILRCV |
| LOCATIONS | LOCATION | LOCATION | LOCSTATUS | LOCAPPR |
| JOBPLAN | JOBPLAN | JPNUM | JPSTATUS | JPACTIVATE |
