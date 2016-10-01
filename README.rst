TODO
====

* Document which time frame the completed orders in chart are allocated.
* Fill time gaps in ``chartData`` where count was 0 and SQL grouping hence
  didn't return a record for this time window.
* Retry query if lock couldn't be acquired in time.
