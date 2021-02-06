
# Changelog

## v4.1

LabTemplate does not require `Labsch` entry anymore.
`group` and `service` attributes may not exist.

## v4.0

**API Changes**
* LabTemplate now requires device identifier for 2nd argument
  Old: db context, analyte name
  New: db context, device identifier, analyte name
  Analyte names are for example: 'SO' for sofia, 'XN' for sysmex

## v3.1

Add method to get all phone numbers associated with Intern

## v3.0

Recode kassenkartei

* new class `klein_tools.kassenkartei.Kassenkartei` (represents Kartei for specific Intern)
* moved free function `klein_tools.kassenkartei.leistung` to new class
* added class to DB context manager
* added `klein_tools.kassenkartei.Kassenkartei.log` method
* added `klein_tools._db_impl.Intern.kartei` method to get Kassenkartei object for Intern

## v2.6

Fix DOB parsing

## v2.5

Added methods to Intern:
* fullname
* age

## v2.4

Workqueue update:
* Added unlock function to return task to queue

## v2.3

Added Queries.

## v2.2

Change telephone join type from JOIN to LEFT JOIN.
Patients are not required to have Stammzusatz record.

## v2.1

Fix missing import

## v2.0

Fix for Connection timeout problem.
Now requires all DB actions to be performed in with-context.

## v1.0

Initial release

Known issues:

* Connection is stored internally and times out.
  This causes the program to cease to function.
