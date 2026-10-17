# Converting IBM Maximo Java MBOs to Python Automation Scripts

**Source**: [IBM Developer Article](https://developer.ibm.com/articles/awb-maximo-java-python-conversion/)  
**Article Title**: Converting IBM Maximo Java MBOs to Python  
**Context**: Guide for transitioning from Java-based Maximo Business Objects (MBOs) to Python automation scripts within IBM Maximo

---

## The Problem: Java Customization Downtime

In Maximo, customers often customize Java code to meet their specific business needs. However, deploying these customizations can cause **downtime**, disrupting workflows and reducing productivity.

### The Solution: Automation Scripts

To address this, **IBM introduced automation scripts in Maximo 7.5**. These scripts allow users to implement custom logic without requiring system downtime, ensuring seamless deployment and continuous availability. This approach enhances efficiency, minimizes disruptions, and provides a more flexible way to customize Maximo.

---

## Benefits of Automation Scripts

### 1. **Customization without Java**
- Customize Maximo without Java skills
- Automation scripts can be written in multiple languages (Python, JavaScript, etc.)

### 2. **Flexible Integration**
- Extend Maximo's functionality without modifying the core system
- No need to modify base Maximo code
- Easier to maintain and upgrade

### 3. **Easy Maintenance**
- Update and manage scripts directly in Maximo without the need for redeployment
- No system restart required
- Changes take effect immediately

### 4. **Zero Downtime Deployment**
- Deploy customizations without disrupting operations
- Continuous availability during updates
- Reduced risk of production issues

---

## Maximo Code Assistant: Simplifying Code Conversion

Many organizations use custom Java code in Maximo, but converting it into automation scripts can be time-consuming and complex. To simplify this process, IBM developed **Maximo Code Assistant**, an AI-powered tool that automatically converts Java code into automation scripts with minimal manual effort.

### Overview

The **Maximo Code Assistant** is an open-source tool designed to simplify the conversion of Maximo Java customizations into Python automation scripts. It leverages **IBM watsonx.ai** to automate the transformation process, ensuring accuracy and efficiency. This repository provides the framework, conversion rules, and examples needed to streamline Maximo automation development.

### Key Benefits

- **Accelerates automation adoption** by reducing conversion time
- **Optimizes code** for better performance
- **Ensures seamless deployment** in Maximo
- **Reduces manual effort** through AI-powered conversion

### Technology Stack

- **watsonx.ai**: IBM's advanced AI platform
- **Large Language Models (LLMs)**: Trained for high-accuracy code conversion
- **Pre-trained models**: Ready-to-use conversion models
- **Advanced prompting techniques**: Generate precise automation scripts tailored to Maximo's environment

### Getting Started

To download and setup the Maximo Automation Script Converter framework, see the [GitHub repository](https://github.com/IBM/maximo-code-assistant).

---

## Framework Overview

The framework enables accurate Java-to-automation script conversion using deep Maximo knowledge and AI-powered processing.

### Key Features

1. **Maximo API Integration**
   - Uses the Maximo API to fetch object and attribute details for precise code generation
   - Provides essential context for accurate conversion

2. **AI-Powered Training**
   - Trained with Maximo custom code and automation script examples for reliable conversion
   - Uses watsonx.ai for intelligent code transformation

3. **Multi-Format Support**
   - Supports `.py` (Python) and `.java` (Java) file formats
   - Handles various Java class types

4. **Intelligent Conversion**
   - Preserves business logic and structure
   - Maintains functionality while improving code quality

---

## Conversion Process

The Maximo Code Assistant follows a systematic conversion process:

### Step 1: Input Processing
- The system accepts a folder with customized Java classes
- Extracts all `.java` files from the input directory

### Step 2: Class Analysis
- Identifies qualified class names from Java files
- These are used as parameters for Maximo API calls

### Step 3: Context Gathering
- The Maximo API fetches object names and attributes
- Provides essential conversion context for accurate transformation

### Step 4: AI-Powered Translation
- The watsonx.ai model translates Java classes into Python automation scripts
- Preserves logic and structure while converting syntax

### Step 5: Script Generation
- The LLM output is combined with Maximo API data
- Creates a ready-to-use automation script with proper context

### Step 6: Output Storage
- The generated `.py` files are stored in a dedicated folder
- Ready for validation and deployment

### Step 7: Validation and Deployment
- Developers validate scripts
- Create a launch point
- Associate relevant attributes/objects
- Specify the event type (run action, validate, init)
- This information is included in script comments for clarity

---

## Optimizing Prompting for LLM Training

### Initial Approach

To train the LLM in watsonx.ai, we explored different approaches:

1. **Example-Based Learning**: Provided examples of Maximo Java customizations alongside their corresponding automation scripts
2. **Rule Definition**: Defined conversion rules
3. **Model Testing**: Tested various models

**Result**: Initial results were unsatisfactory.

### Improved Approach

To improve accuracy, we refined our prompt by:

1. **Clear Conversion Rules**: Incorporated detailed conversion rules
2. **Multiple Examples**: Included multiple Java-to-Python examples
3. **Combined Examples**: Added combined examples of customized Java classes and their corresponding automation scripts to reinforce the rules

### Model Selection

Using this optimized prompt, we tested multiple models and found that **mixtral-8x7b-instruct-v01** delivered the most accurate results.

---

## Conversion Rules for Maximo Java to Python Automation Scripts

### Rule 1: Remove Class Definitions

Maximo automation scripts don't require class definitions. Remove Java class structures and place the logic directly in the script.

**Java:**
```java
public class FldWorkTypeCust extends FldWorkType {
    public FldWorkTypeCust(MboValue mbv) throws MXException {
        super(mbv);
    }
    
    @Override
    public void action() throws MXException {
        super.action();
    }
}
```

**Python:**
```python
# Main script logic starts here
worktype = mbo_value.getString("WORKTYPE")
```

---

### Rule 2: Variable Initialization Based on Data Type

Convert Java variable assignments to Python equivalents using Maximo methods.

#### String Variables

**Java:**
```java
String woStatus = this.getMboValue().getString();
```

**Python:**
```python
wo_status = mbo_value.getString("STATUS")
```

#### Integer Variables

**Java:**
```java
int wopriority = this.getMboValue().getInt();
```

**Python:**
```python
wopriority = mbo.getInt("WOPRIORITY")
```

#### Date Variables

**Java:**
```java
Date invoiceDate = invoice.getDate("invoicedate");
```

**Python:**
```python
invoicedate = mbo.getDate("invoicedate")
```

---

### Rule 3: Setting Values and Field Flags

#### Import Required Package

**Java:**
```java
import psdi.mbo.MboConstants;
```

**Python:**
```python
from psdi.mbo import MboConstants
```

#### Setting a Field Value

**Java:**
```java
woMbo.setValue("ACTMATCOST", totalCost, NOVALIDATION_AND_NOACTION);
```

**Python:**
```python
mbo.setValue("ACTMATCOST", total_cost, MboConstants.NOVALIDATION_AND_NOACTION)
```

#### Setting a Field Flag

**Java:**
```java
woRemote.setFieldFlag(worktype, READONLY, true);
```

**Python:**
```python
mbo.setFieldFlag(worktype, MboConstants.READONLY, True)
```

---

### Rule 4: Throwing Errors

Use Maximo's service method for error handling.

#### Import Required Package

**Java:**
```java
import psdi.util.MXException;
```

**Python:**
```python
from psdi.util import MXException
```

#### Example

**Java:**
```java
throw new MXApplicationException("custerrgrp", "custerrkey");
```

**Python:**
```python
service.error("custerrgrp", "custerrkey")
```

---

### Rule 5: Getting System Information (e.g., System Date)

#### Import Required Package

**Java:**
```java
import psdi.server.MXServer;
```

**Python:**
```python
from psdi.server import MXServer
```

#### Example

**Java:**
```java
curdate = MXServer.getMXServer().getDate();
```

**Python:**
```python
cur_date = MXServer.getMXServer().getDate()
```

---

### Rule 6: Handling Errors with Parameters

If the Java code uses parameters in error handling, convert it to Python as follows:

**Java:**
```java
Object[] params = {"Invoice Date"};
throw new MXApplicationException("asset", "AsOfDateNotValid", params);
```

**Python:**
```python
params = ["Invoice Date"]
service.error("asset", "AsOfDateNotValid", params)
```

---

### Rule 7: Changing Status

Use the Python equivalent method for changing an object's status.

**Java:**
```java
((PORemote) po).changeStatus("APPR", MXServer.getMXServer().getDate(), "Auto-approved by script");
```

**Python:**
```python
mbo.changeStatus("APPR", MXServer.getMXServer().getDate(), "Auto-approved by script")
```

---

### Rule 8: Super Method Calls

Skip Java super method calls. Simply implement the required logic directly.

**Java:**
```java
super.action();
```

**Python:**
```python
# No equivalent needed, directly implement logic
```

---

### Rule 9: No Need for mbo_value.getMbo()

Remove explicit calls to `getMbo()` when working with `mbo_value`.

**Java:**
```java
MboRemote woMbo = this.getMboValue().getMbo();
String woStatus = this.getMboValue().getString();
```

**Python:**
```python
wo_status = mbo.getString("STATUS")
```

---

## Complete Conversion Prompt Template

### Role

You are a skilled Maximo developer experienced in automation scripts. Your task is to analyze the given Maximo Java customization class and convert it into an equivalent Python automation script. The script should maintain the logic and structure of the Java code while following the specified conversion rules. Ensure the script is optimized, clean, and includes meaningful comments for clarity.

### Task: Convert Maximo Java Code to Python Automation Script

#### Objective

Convert the following Maximo Java class into a Python automation script using the defined conversion rules. Ensure the script maintains the logic and functionality of the original Java class while improving readability, using descriptive variable names, and including comments for clarity.

---

## Example: Complete Java to Python Conversion

### Input: Maximo Java Code

```java
package cust.app;

import java.rmi.RemoteException;
import java.util.Date;
import psdi.app.financial.FldPartialGLAccount;
import psdi.app.invoice.FldInvoiceInvoiceDate;
import psdi.app.ticket.FldTkTicketId;
import psdi.app.workorder.FldWOPriority;
import psdi.app.workorder.FldWorkType;
import psdi.mbo.Mbo;
import psdi.mbo.MboRemote;
import psdi.mbo.MboSetRemote;
import psdi.mbo.MboValue;
import psdi.mbo.MboValueAdapter;
import psdi.plusd.app.workorder.PlusDWORemote;
import psdi.server.MXServer;
import psdi.util.MXApplicationException;
import psdi.util.MXException;

public class CombinedCustomClass extends MboValueAdapter {
    public CombinedCustomClass(MboValue mbv) {
        super(mbv);
    }

    @Override
    public void action() throws MXException, RemoteException {
        Mbo mbo = this.getMboValue().getMbo();
        String attributeName = this.getMboValue().getName();
        Date sysDate = MXServer.getMXServer().getDate();

        if (attributeName.equalsIgnoreCase("STATUS")) {
            handleWorkOrderStatus(mbo);
        } else if (attributeName.equalsIgnoreCase("WORKTYPE")) {
            handleWorkType(mbo);
        } else if (attributeName.equalsIgnoreCase("GLACCOUNT")) {
            handleGLAccount(mbo, sysDate);
        } else if (attributeName.equalsIgnoreCase("WOPRIORITY")) {
            handleWOPriority(mbo);
        } else if (attributeName.equalsIgnoreCase("INVOICEDATE")) {
            handleInvoiceDate(mbo, sysDate);
        } else if (attributeName.equalsIgnoreCase("TICKETID")) {
            handleTicketId(mbo);
        }
    }

    private void handleWorkOrderStatus(Mbo mbo) throws RemoteException, MXException {
        String status = this.getMboValue().getString();
        if (status.equalsIgnoreCase("COMP")) {
            MboSetRemote materialSet = mbo.getMboSet("SHOWACTUALMATERIAL");
            MboRemote material = materialSet.moveFirst();
            double totalCost = 0;
            while (material != null) {
                totalCost += material.getDouble("LINECOST");
                material = materialSet.moveNext();
            }
            mbo.setValue("ACTMATCOST", totalCost, Mbo.NOVALIDATION_AND_NOACTION);
        }
    }

    private void handleWorkType(Mbo mbo) throws RemoteException, MXException {
        String workType = this.getMboValue().getString();
        if (workType.equalsIgnoreCase("EM")) {
            mbo.setValue("WOPRIORITY", "1", Mbo.NOVALIDATION_AND_NOACTION);
            mbo.setFieldFlag("WORKTYPE", Mbo.READONLY, true);
        }
    }

    private void handleGLAccount(Mbo mbo, Date sysDate) throws RemoteException, MXException {
        String glAccount = this.getMboValue().getString();
        String workType = mbo.getString("WORKTYPE");
        if (glAccount != null && workType.equalsIgnoreCase("PM")) {
            ((PlusDWORemote) mbo).changeStatus("APPR", sysDate, "Work order Status moved to APPR");
        }
    }

    private void handleWOPriority(Mbo mbo) throws RemoteException, MXException {
        int priority = this.getMboValue().getInt();
        if (priority > 5) {
            throw new MXApplicationException("custerrgrp", "custerrkey");
        }
    }

    private void handleInvoiceDate(Mbo mbo, Date curDate) throws RemoteException, MXException {
        Date invoiceDate = mbo.getDate("invoicedate");
        if (invoiceDate.before(curDate)) {
            Object[] params = { "Invoice Date" };
            throw new MXApplicationException("asset", "AsOfDateNotValid", params);
        }
    }

    private void handleTicketId(Mbo mbo) throws RemoteException, MXException {
        String app = mbo.getThisMboSet().getApp();
        if (app != null && app.equalsIgnoreCase("SR")) {
            mbo.setValue("REPORTEDPRIRITY", 2, Mbo.NOACCESSCHECK);
        }
    }
}
```

### Output: Python Automation Script

```python
from psdi.util import MXException, MXApplicationException
from psdi.mbo import MboConstants
from psdi.server import MXServer

try:
    attribute_name = mbo_value.getName()
    sys_date = MXServer.getMXServer().getDate()

    if attribute_name == "STATUS":
        totalCost = 0
        woStatus = mbo.getString("STATUS")
        if woStatus == "COMP":
            childMatUseTransSet = mbo.getMboSet("SHOWACTUALMATERIAL")
            if not childMatUseTransSet.isEmpty():
                childMatUseTransMbo = childMatUseTransSet.moveFirst()
                while childMatUseTransMbo is not None:
                    linecost = childMatUseTransMbo.getDouble("LINECOST")
                    totalCost += linecost
                    childMatUseTransMbo = childMatUseTransSet.moveNext()
                mbo.setValue("ACTMATCOST", totalCost, MboConstants.NOVALIDATION_AND_NOACTION)

    elif attribute_name == "WORKTYPE":
        worktype = mbo.getString("WORKTYPE")
        if worktype == "EM":
            mbo.setValue("WOPRIORITY", "1", MboConstants.NOVALIDATION_AND_NOACTION)
            mbo.setFieldFlag("WORKTYPE", MboConstants.READONLY, True)

    elif attribute_name == "GLACCOUNT":
        woGlAccount = mbo.getString("GLACCOUNT")
        woWorkType = mbo.getString("WORKTYPE")
        if woGlAccount and woWorkType == "PM":
            mbo.changeStatus("APPR", sys_date, "Workorder Status moved to APPR")

    elif attribute_name == "WOPRIORITY":
        wopriority = mbo.getInt("WOPRIORITY")
        if wopriority > 5:
            raise MXApplicationException("custerrgrp", "custerrkey")

    elif attribute_name == "INVOICEDATE":
        curDate = sys_date
        invoiceDate = mbo.getDate("INVOICEDATE")
        if invoiceDate < curDate:
            raise MXApplicationException("asset", "AsOfDateNotValid", ["Invoice Date"])

    elif attribute_name == "TICKETID":
        app = mbo.getThisMboSet().getApp()
        if app and app.upper() == "SR":
            mbo.setValue("REPORTEDPRIORITY", 2, MboConstants.NOACCESSCHECK)

except MXException as e:
    scriptLog.error("Got an MXException: " + str(e))
except Exception as e:
    scriptLog.error("Got an Exception: " + str(e))
```

---

## Testing the Code Conversion Framework

### Test Scenario

If we input a Java class that updates the Work Order (WO) status to "APPR" when the GL account is updated for a PM-type WO, the framework processes it as follows:

### Framework Input

```java
package cust.app.workorder;

import java.rmi.RemoteException;
import java.util.Date;
import psdi.app.financial.FldPartialGLAccount;
import psdi.plusd.app.workorder.PlusDWORemote;
import psdi.mbo.MboValue;
import psdi.server.MXServer;
import psdi.util.MXException;

public class FldGLAccNew extends FldPartialGLAccount {
    public FldGLAccNew(MboValue mbv) {
        super(mbv);
        // TODO Auto-generated constructor stub
    }

    @Override
    public void action() throws RemoteException, MXException {
        super.action();
        PlusDWORemote woMbo = (PlusDWORemote) this.getMboValue().getMbo();
        String woGlAccount = this.getMboValue().getString();
        String woWorkType = this.getMboValue("WORKTYPE").getString();
        Date sysdate = MXServer.getMXServer().getDate();

        if (woGlAccount != null && woWorkType == "PM") {
            woMbo.changeStatus("APPR", sysdate, "Workorder Status moved to APPR");
        }
    }
}
```

### Framework Output

```python
# Class name: psdi.app.financial.FldPartialGLAccount
# This automation script has been generated using watsonx.ai.
# The required parameters to create this in Maximo Environment are as follows:
# Provided class name is deployed multiple times here is the list of object names and attribute names [{'attribute_name': 'GLACCOUNT', 'object_name': 'INCIDENT'}]
# LAUNCHPOINT: ATTRIBUTE
# EVENTTYPE: RUN ACTION

from psdi.util import MXException, MXApplicationException
from psdi.mbo import MboConstants
from psdi.server import MXServer

try:
    mbo_value = mbo.getMboValue("GLACCOUNT")
    mbo_worktype = mbo.getString("WORKTYPE")
    sys_date = MXServer.getMXServer().getDate()

    if mbo_value and mbo_worktype == "PM":
        mbo.changeStatus("APPR", sys_date, "Workorder Status moved to APPR")

except MXException as e:
    scriptLog.error("Got an MXException: " + str(e))
except Exception as e:
    scriptLog.error("Got an Exception: " + str(e))
```

---

## Conclusion

This approach enables efficient and accurate conversion of Maximo Java code into Python automation scripts. By systematically extracting object names, attributes, and logic, the framework ensures seamless adaptation to Maximo's Python environment while preserving functionality and minimizing errors.

### Current Scope

Currently, this solution is designed and tested for **field-level classes** in Maximo. It can be extended to support other class types, such as:

- Object-level classes
- Integration classes
- Action classes
- Cron classes

Additional testing and customization would be required for these extensions.

### Key Benefits

- **Automated Conversion**: Reduces manual conversion effort significantly
- **Accuracy**: AI-powered conversion ensures high accuracy
- **Consistency**: Standardized conversion rules ensure consistent output
- **Efficiency**: Faster conversion process compared to manual coding
- **Maintainability**: Generated scripts follow best practices

---

## Acknowledgements

I would like to extend my thanks to **Amitabha Kanjilal** and **Satish Somanna Narasimha** for their guidance and support in developing this solution.

---

## Additional Resources

- [IBM Maximo Automation Scripts Documentation](https://www.ibm.com/docs/en/maximo)
- [Maximo REST API Documentation](https://developer.ibm.com/apis/maximo--maximo-manage-rest-api)
- [Maximo Code Assistant GitHub Repository](https://github.com/IBM/maximo-code-assistant)
- [IBM watsonx.ai Platform](https://www.ibm.com/products/watsonx-ai)
- [Maximo Community Forums](https://community.ibm.com/community/user/aiops/communities/community-home)

---

## References

- **Source Article**: [Converting IBM Maximo Java MBOs to Python](https://developer.ibm.com/articles/awb-maximo-java-python-conversion/)
- **IBM Maximo Documentation**: Official Maximo documentation and guides
- **Python Documentation**: Python language and library documentation
- **Maximo Code Assistant**: Open-source conversion framework

---

**Document Version**: 2.0  
**Last Updated**: Based on comprehensive IBM Developer article content  
**Status**: Complete reference document for Java to Python conversion in Maximo using Maximo Code Assistant
