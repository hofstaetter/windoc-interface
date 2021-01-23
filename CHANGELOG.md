
# v2.4

Workqueue update:
* Added unlock function to return task to queue

# v2.3

Added Queries.

# v2.2

Change telephone join type from JOIN to LEFT JOIN.
Patients are not required to have Stammzusatz record.

# v2.1

Fix missing import

# v2.0

Fix for Connection timeout problem.
Now requires all DB actions to be performed in with-context.

# v1.0

Initial release

Known issues:

* Connection is stored internally and times out.
  This causes the program to cease to function.
