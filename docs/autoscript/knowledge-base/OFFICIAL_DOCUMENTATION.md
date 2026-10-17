# IBM Maximo Automation Script - Official Documentation (Local Copy)

**Source**: IBM Maximo Automation Script Documentation  
**URL**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/  
**Last Updated**: Based on available documentation as of 2024

**Note**: This is a local copy of key documentation for offline reference. Always refer to the official documentation for the most up-to-date information.

---

## Table of Contents

1. [Script Components](#script-components)
2. [Implicit and Explicit Variables](#implicit-and-explicit-variables)
3. [Variable Binding Metadata](#variable-binding-metadata)
4. [Launch Points](#launch-points)
5. [Script and Launch Point Creation](#script-and-launch-point-creation)
6. [Script and Launch Point Maintenance](#script-and-launch-point-maintenance)
7. [Variables and Bindings](#variables-and-bindings)
8. [Activating and Deactivating Scripts](#activating-and-deactivating-scripts)
9. [Best Practices](#best-practices)

---

## Script Components

### Script/Launch Point Creation

Script and Launch point creation are done using wizards that are available from the **List** tab in the Automation Script application. You can launch the Automation Script application from the **GoTo → System Configuration → Autoscript** menu.

In the **List** tab drop down actions list, you can see the following wizards:

| Script wizards                                     |
| -------------------------------------------------- |
| Create a vanilla script without any launch point.  |
| Create scripts with Object launch point.           |
| Create scripts with Attribute launch point.        |
| Create scripts with Action launch point.           |
| Create scripts with custom condition launch point. |
| Create scripts for Integration.                    |

These wizards will guide you through the process of creating a script and optionally associating launch points with it.

### Script and Launch Point Maintenance

After the script and launch point has been created, you can use the Automation Script application for maintenance. Maintenance can be done using the **Main, Variables, Launch point** tabs in the Automation Script application. You can add or update the variables and their bindings as well as the bindings at the launch point level, if they are overridable. You cannot delete variables unless none of the launch points refer to that variable.

---

## Variables and Bindings

Scripts use variables to interact with Maximo. Variables are either IN, INOUT, or OUT. These variables follow the classical definition where:

- **IN**: Pass-by-value - Modifying IN variables in the script has no impact outside the script
- **INOUT**: Pass-by-reference - The script can modify INOUT variables
- **OUT**: Pass-by-reference - The script can modify OUT variables

Variables can be bound to a Maximo artifact including:
- A MBO attribute
- A maxvar
- A Maximo system property
- A literal value which is not related to any Maximo artifact

Variables bound to a maxvar or a system property are always IN variables as the script cannot modify them.

**Variable Data Type Rules:**
- Variable data type for MBO attributes is driven by the MBO attribute datatype
- Variables bound to maxvar and system properties are always String variables
- Variables bound to literal values can define data type by specifying "literaldatatype" attribute in the autoscriptvars table

**Supported Literal Data Types:**
- ALN
- INTEGER
- SMALLINT
- DECIMAL
- YORN
- DATETIME
- FLOAT

You can define variable bindings at the script level or the launch point level if the definition at the script level allows override of that value at the launch point level.

### Setting MBO Attributes with Flags

Another important aspect of the OUT and INOUT variables is how their values can be set back to the MBOs. You can set MBO attributes with flags that control behavior:

- **NOACTION flag**: Determines if modifying the value of the MBO attribute will call the field validations action routine
- **NOVALIDATION flag**: Determines if modifying the value of the MBO attribute will call the field validations validate routine
- **NOACCESSCHECK flag**: Determines if the Action/Validation routine of the MBO attributes are called

You can set an MBO attribute with any combination of these flags. You can enable these settings from the script or launch point creation wizards and Automation Script application.

---

## Variable Binding Metadata

The following table explains binding metadata usage:

| Binding metadata        | Type    | Description                                                                                                                                                                                                                             | Applicability          |
| ----------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **Suppress Validation** | Boolean | MBO attributes will be set with the NOVALIDATION flag, which determines if modifying the value of the MBO attribute will call the field validations validate routine (false) or not call the field validations validate routine (true). | For attribute bindings |
| **Suppress Action**     | Boolean | MBO attributes will be set with the NOACTION flag, which determines if modifying the value of the MBO attribute will call the field validations action routine (false) or not call the field validations action routine (true).         | For attribute bindings |
| **Suppress Access Control** | Boolean | MBO attributes will be set with the NOACCESSCHECK flag, which determines if the MBO attribute value can be modified irrespective of whether the attribute is readonly (true) or not (true/false).                                       | For attribute bindings |

---

## Implicit and Explicit Variables

### Explicit Variables

Explicit variables are explicitly defined and bound in the variables page.

### Implicit Variables

Implicit variables are not explicitly defined in the variables page and are provided to you behind the scenes by the framework. Implicit variables follow the convention over configuration pattern where the framework will intelligently inject variables at run time which might otherwise have needed JAVA coding to fetch and set.

Some implicit variables are injected based on how the explicit variables are defined and some are injected irrespectively.

### Implicit Variables Table

| Name        | Type                                       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Applicability                                                                                       |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `app`         | String                                     | The name of the Maximo application which initiated the script execution.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | All launch points dealing with an MBO or MBOSET                                                     |
| `user`        | String                                     | userid of the user whose action initiated the script execution.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | All launch points dealing with an MBO or MBOSET                                                     |
| `mbo`         | psdi.mbo.Mbo                               | The current MBO in the context of the script execution. For example, in case of the Object Launch Point this will be the MBO, which is generating the events for the scripting framework. For attribute launch point this is the attributes owner MBO. For Action launch point this may be the Escalation or workflows MBO.                                                                                                                                                                                                                                                               | All launch points dealing with an MBO or MBOSET                                                     |
| `mboname`     | String                                     | The name of the current MBO in the context of the script execution.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | All launch points dealing with an MBO or MBOSET                                                     |
| `errorkey`    | String                                     | This variable is for throwing MXExceptions from the script without having to explicitly import or refer to that API. This refers to the error key in the MXException. It works together with the errorgroup and the params implicit variables. The MXExceptions API is the standard way to throw Exceptions from Maximo-based components. The exception message is translated, which is the main advantage of using this API instead of a standard Java Exception, which is not going to be translated. **Its usage is deprecated and replaced by the service variable's error(..) function** | All launch points                                                                                   |
| `errorgroup`  | String                                     | Its usage is the same as the errorkey. It points to the error group of the MXException. Together with the errorkey it helps uniquely point to an error message in the Maximo message repository. **Its usage is deprecated and replaced by the service variable's error(..) function**                                                                                                                                                                                                                                                                                                        | All launch points                                                                                   |
| `interactive` | boolean                                    | It is a boolean variable indicating whether the script is executed in an interactive or UI session \[value true\] or a background session \[for example, Integration\]. This reflects the value of userInfo.isInteractive().                                                                                                                                                                                                                                                                                                                                                              | All launch points                                                                                   |
| `evalresult`  | boolean                                    | This is a boolean variable of type OUT to indicate the result of the condition evaluation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Condition launch point and publish channel event filters                                            |
| `onadd`       | boolean                                    | This boolean variable indicates whether the MBO in the script is added \[new MBO – value true\] or not. The script developer can use this for conditional actions or validations based on the state of the MBO.                                                                                                                                                                                                                                                                                                                                                                           | All launch points or callbacks where MBO/MBOSET is involved. Mostly useful for Object launch point  |
| `onupdate`    | boolean                                    | Boolean variable indicates where the MBO in the script is updated \[exiting MBO – value true\] or not. The script developer can use it for conditional actions or validations based on the state of the MBO.                                                                                                                                                                                                                                                                                                                                                                              | All launch points or callbacks where MBO/MBOSET is involved. Mostly useful for Object launch points |
| `ondelete`    | boolean                                    | Boolean variable indicating whether the MBO in the script context is deleted \[value true\] or not.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | All launch points or callbacks where mbo/mboset is involved. Mostly useful for Object launch point  |
| `action`      | String                                     | The name of the Action that was generated from the Action Launch Point wizard.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Action Launch Point                                                                                 |
| `scriptName`  | String                                     | The name of the Script that is executed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | All Launch points                                                                                   |
| `launchPoint` | String                                     | The name of the launch point for which the script is executed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | All Launch points                                                                                   |
| `scriptHome`  | psdi.mbo.Mbo                               | This is the same as the implicit variable MBO. It allows backward compatibility with ICD scripts.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Action Launch points                                                                                |
| `wfinstance`  | psdi.workflow.WFInstance                   | The workflow instance MBO.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Action Launch Point – only when the Action is launched from a workflow.                             |
| `service`     | com.ibm.tivoli.maximo.script.ScriptService | The global implicit var available to all scripts.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | All Launch points and callbacks                                                                     |
| `listMboSet`  | psdi.mbo.MboSetRemote                      | This is used for setting the lookup MBOSET from a lookup script in attribute launch point.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Attribute Launch points - lookup scripts.                                                           |
| `srcKeys`     | String\[\]                                 | Used for mapping lookup MBO key to target MBO key (targetKeys).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Attribute Launch points - lookup scripts.                                                           |
| `targetKeys`  | String\[\]                                 | Used for mapping target MBO key to lookup MBO key (srcKeys).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Attribute Launch points - lookup scripts.                                                           |

### Implicit Variables Based on Explicit Variables

Some implicit variables are injected into the script based on the explicitly defined variables. The following table describes the implicit variables that are based on explicitly defined variables whose binding type is an MBO attribute. There are no implicit variables for explicitly defined variables of other binding types like Literals, Maxvars, and System properties.

**Note**: The assumption is that "var" is the explicitly defined variable that binds to an MBO attribute.

| Name          | Type                                                  | Description                                                                                                                      | Applicability                                                                                                                      |
| ------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `var_required` | boolean                                               | Required flag of the MBO attribute that var binds to.                                                                            | All launch points. The script can modify it if the var is OUT or INOUT.                                                            |
| `var_readonly` | boolean                                               | Readonly flag of the MBO attribute that var binds to.                                                                            | All launch points. The script can modify it if the var is OUT or INOUT.                                                            |
| `var_hidden`   | boolean                                               | Hidden flag of the MBO attribute that var binds to.                                                                              | All launch points. The script can modify if the var is OUT or INOUT.                                                               |
| `var_internal` | Same type as the MBO attribute to which var binds to. | For synonym domain kind of MBO attributes \[like status\] this represents the internal \[maxvalue\] value for the MBO attribute. | All launch points. Applicable only if var is bound to a MBO attribute that binds to a synonym domain. The script cannot modify it. |
| `var_previous` | Same type as the MBO attribute                        | The previous value of the MBO attribute ie the value just before the attribute value got changed.                                | Attribute launch points – applicable only for the attribute that generated the event. The script cannot modify it.                 |
| `var_initial`  | Same type as the MBO attribute                        | The initial value of the MBO attribute ie the value assigned to that attribute when the MBO was initialized.                     | All launch points. The script cannot modify it.                                                                                    |
| `var_modified` | boolean                                               | Indicates whether the MBO attribute to which the variable var binds to has been modified or not.                                 | All launch points. The script cannot modify it.                                                                                    |

---

## Launch Points

**Launch points** are application customization points. Launch points define which application artifact the user wants to customize by attaching the script to that point. In effect, the script is executed in the context of a launch point.

For example:
- If you want to customize the Asset MBO's initialization routine, use the keywords: **Asset MBO** & **initialization routine**
- If you want to customize the Asset MBO's purchaseprice attribute field validation routine, use the keywords: **Asset MBO**, **purchaseprice attribute**, and **field validation routine**

Essentially, a launch point is a configuration to identify the application point to customize.

### Multiple Launch Points

A script can be associated with one or more launch points simultaneously. For example:
- A generic site-level validation script can be associated with all site level objects where each association is defined as an individual launch point
- A script can be associated with a single launch point

**Important**: After the first association is completed between a script and a launch point, all subsequent launch points have to be the same type as the first. For example, a script associated with the Object launch point cannot be associated again with another attribute launch point.

### Supported Launch Points

The following launch points are currently supported by the scripting framework:

1. **MBO initialization and save point logic** or **Object launch point**
2. **MBO attribute value modification – validation and action logic** or **Object attribute launch point**
3. **Actions**, which are used by many other components like Workflow, Escalation, UI Menu, UI Buttons or **Action launch point**
4. **Custom conditions** used by Workflow conditions, Conditional UI and others or **custom condition launch point**

**Note**: Launch points and callbacks are the first artifacts to consider when customizing an application.

---

## Activating and Deactivating Scripts

Scripts can be activated or deactivated from the **Launch Point** tab of the Automation Scripting application or from the Script main page.

- **Deactivation from the main script**: Will deactivate the script for all launch points of that script
- **Deactivation from launch point**: Only deactivates that particular launch point. All other active launch points should continue working as usual

Maximo will not invoke a deactivated script. For example, if an Attribute launch point is deactivated, the script for that launch point will not be invoked if the value of that MBO attribute changes.

Activating and deactivating scripts is a very useful tool for debugging issues with the application behavior and can take the script out of the equation temporarily to test the application without customization.

**Important**: The autoscript status attribute value has no significance on how the scripting framework will or will not invoke the script.

---

## Usage Examples

### Using Implicit Variables

```python
# Check if running in interactive mode
if interactive:
    # Code that should only run in UI session
    service.error('Field Name', 'error message')

# Check MBO state
if onadd:
    # Code for new MBO
    mbo.setValue("FIELDNAME", defaultValue, MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION)

if onupdate:
    # Code for updated MBO
    pass

if ondelete:
    # Code for deleted MBO
    pass

# Get current application
appName = app  # String - Current Maximo application name

# Get current user
currentUser = user  # String - Current user ID

# Access MBO
currentMbo = mbo  # psdi.mbo.Mbo - Current MBO object
mboName = mboname  # String - Current MBO name

# Use service object (recommended over errorkey/errorgroup)
service.error('Field Name', 'error message')
service.error('Field Name', 'error message', ['param1', 'param2'])
service.warning('Warning message')
```

### Using Implicit Variables Based on Explicit Variables

```python
# If you have an explicit variable "status" bound to an MBO attribute

# Check if field is required
if status_required:
    # Field is required
    pass

# Check if field is readonly
if status_readonly:
    # Field is readonly
    pass

# Check if field is hidden
if status_hidden:
    # Field is hidden
    pass

# Get internal value (for synonym domains)
internalValue = status_internal  # Internal maxvalue

# Get previous value
previousValue = status_previous  # Value before change (Attribute launch points only)

# Get initial value
initialValue = status_initial  # Value when MBO was initialized

# Check if field was modified
if status_modified:
    # Field has been modified
    pass
```

---

## Best Practices

**Source**: [IBM Maximo Automation Script Best Practices](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/bestpractice/overview/)

Scripting allows you to extend Maximo business logic using Python/JS or any other JSR223 compliant scripting language. All the script code gets compiled to Java bytecode and are cached as part of Maximo runtime caches. When the script is invoked, it is the cached bytecode that is executed by the JVM using the JSR223 bridge. Since the script code executes in the same thread as other Maximo business logic (written in Java), a poorly written script code can impact the performance of the system negatively. In general you should follow the Maximo Performance guidelines because scripting in the end is equivalent to Maximo custom code, to avoid common mistakes.

### 1. Choosing the Right Launch Point and Event

Launch points are script trigger points. Often, choosing the right launch point can help avoid certain performance issues in scripting.

**Example: Attribute Launch Point vs Object Launch Point**

In Maximo 7.5 scripting release, there was no support for attribute value initialization. This led many script developers to use the Object Launch Point (OLP) Init event to initialize the MBO attribute values. Though functionally was not affected, it potentially could lead to performance issues when selecting a bunch of MBOs (in **List** tab or APIs/MIF, Escalations). The OLP init event script gets executed for every MBO that is selected in the MboSet, even though the attribute whose value was getting initialized by the script was not even used or shown.

**Solution**: Change the Object launch point to Attribute launch point for the Initialize Value event.

```python
# Attribute Launch Point - Initialize Value
# This script only runs when the attribute is actually referenced
if priority is not None:
    thisvalue = 2 * priority
```

The MBO framework will invoke this script only when this attribute is referred to by the code or the UI.

**Example: Integration Event Filters**

For Integration skipping events, use the Publish Channel Event Filter scripting which gets invoked right when the event is triggered and much before any serialization of MBOs happen, instead of user exit scripting.

```python
# Publish Channel Event Filter - runs before serialization
if service.getMbo().getString("status") == "APPR":
    evalresult = False
else:
    evalresult = True
```

### 2. Avoid Costly Object Init Events if Invoked from List Tab

You may want to do costly Object init scripts only when the object is initialized from the **Main** tab (UI) and not from the **List** tab.

```python
from psdi.common.context import UIContext

if UIContext.getCurrentContext() is not None and UIContext.isFromListTab() == False:
    # Costly initialization code here
    # This only runs when not from List tab
    pass
```

### 3. Watch Out for Conflicting Launch Point Event Scripts

Scripting framework allows attaching multiple scripts to the same launch point event. This poses a problem if the script code expects to execute it in a certain order before or after certain other scripts in the same launch point event.

**Problem**: Since the Maximo event topic is an un-ordered map, the events are triggered without a fixed order. This can potentially cause issues if the order dependency is not managed properly.

**Solutions**:
1. **Combine scripts**: Evaluate the reason to attach multiple scripts for the same launch point event and evaluate if it makes more sense to combine them into one script.
2. **Remove dependencies**: Make sure there is no dependency between the scripts.

### 4. Avoid Calling Save in Middle of a Transaction

This is a common coding pattern seen in scripts that can cause problems to Maximo transactions and event firing.

**Best Practice**: Ideally, when a Maximo transaction is in progress, the script should try to be part of that encompassing transaction. The MBOs created or updated by a script are automatically part of the encompassing transaction as long as those were created from the script launch point MBO or any related MBO.

**Problem**: If you create an MBO using the `MXServer.getMXServer().getMboSet("...")` API, it would be outside the encompassing transaction unless you add it explicitly.

**Solution**: Add the MboSet to the encompassing transaction:

```python
# Create MBO outside the current transaction
newMboSet = MXServer.getMXServer().getMboSet("OBJECTNAME", userInfo)

# Add it to the encompassing transaction
mbo.getMXTransaction().add(newMboSet)
```

### 5. Calling MboSet.count() Multiple Times

**Problem**: It is a common programming mistake in the scripts when checking the count of an MboSet multiple times. The `count()` call ends up firing an SQL every time it is called.

**Bad Code**:
```python
if mboset.count() <= 1:
    service.log("skipping this as count is " + mboset.count())
```

**Good Code**:
```python
# Call count() once and store the value
cnt = mboset.count()
if cnt <= 1:
    service.log("skipping this as count is " + cnt)
```

**Best Practice**: Invoke `count()` once, store the value in a variable, and reuse that variable for subsequent code flow.

### 6. Closing the MboSet

**Important**: Maximo MBO framework always releases the MboSets created after a transaction is complete. This is true as long as all the MboSets were created as a related set to launch point MBO or any of it related MBOs.

**Problem**: If however the MboSet is created using the `MXServer.getMXServer().getMboSet(..)` API, the script code is responsible for closing and clearing that MboSet.

**Solution**: Use try-finally block to ensure cleanup:

```python
mboset = None
try:
    mboset = MXServer.getMXServer().getMboSet("OBJECTNAME", userInfo)
    # Use mboset here
    pass
finally:
    if mboset is not None:
        mboset.cleanup()
```

**Why**: If this is not done, it tends to start building up and may result in OOM (Out of Memory) errors.

### 7. Avoid the Mozilla Compatibility Script for Nashorn

**Recommendation**: Moving from Rhino (Java 7) to Nashorn (Java 8) is recommended for performance reasons. Nashorn performs better in Java 8 compared to Rhino.

**Warning**: Leveraging the Mozilla compatibility script with Nashorn can result in poor performance in Java 8.

### 8. Check if Logging is Enabled Before Logging

**Problem**: Logging is often done inside the script without checking the log level. This can impact performance:

```python
# BAD - This calls mboset.count() even if logging is disabled
service.log("count of mbos " + mboset.count())
```

This would unfortunately result in `mboset.count()` being called, even though the script logging is disabled.

**Solution 1**: Check log level before logging (all versions):

```python
from psdi.util.logging import MXLoggerFactory

logger = MXLoggerFactory.getLogger("maximo.script")
debugEnabled = logger.isDebugEnabled()

if debugEnabled:
    service.log("count of mbos " + mboset.count())
```

**Solution 2**: Use service.isLoggingEnabled() (Maximo 7.6.1.2+):

```python
if service.isLoggingEnabled():
    service.log("count of mbos " + mboset.count())
```

### Additional Best Practices

1. **Use `service.error()` instead of `errorkey`/`errorgroup`**: The errorkey and errorgroup implicit variables are deprecated. Always use `service.error()` for error handling.

2. **Check interactive mode**: Always check the `interactive` variable before performing operations that should only run in UI sessions.

3. **Use MBO state flags**: Use `onadd`, `onupdate`, and `ondelete` flags to perform conditional logic based on MBO state.

4. **Use implicit variables for field flags**: Use `var_required`, `var_readonly`, `var_hidden` implicit variables to check and modify field flags.

5. **Activate/deactivate for debugging**: Use script activation/deactivation to debug issues without modifying code.

6. **Use MboConstants flags**: Always use `MboConstants.NOACCESSCHECK | MboConstants.NOVALIDATION` instead of numeric constants like `2L` or `11L`.

7. **Always close MBO sets**: Always close MBO sets created using `MXServer.getMXServer().getMboSet()` to prevent memory leaks.

8. **Avoid multiple count() calls**: Store the result of `count()` in a variable and reuse it.

9. **Choose appropriate launch points**: Use Attribute launch points for field initialization instead of Object launch points when possible.

10. **Check context before costly operations**: Use `UIContext.isFromListTab()` to avoid costly operations in List tab.

---

## Additional Resources

- **Official Documentation**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/
- **Components Reference**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/introduction/components
- **Best Practices**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/bestpractice/overview/
- **Project Patterns Reference**: See `maximo_script_patterns_reference.md`
- **Utility Library**: See `maximo_utility_library.py`

---

**Documentation Source**: IBM Maximo Automation Script Documentation  
**License**: Refer to original IBM documentation for licensing information  
**Last Updated**: Based on available documentation as of 2024

