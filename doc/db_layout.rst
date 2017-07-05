Design
======
* All order data is to be retrieved from ``order_str`` and not from
  ``order_hdr``.
* "Released" orders are orders where ``sys-id != null and order_str.os_status
  not in (P, T) and oh_amend = today``.
* "Packed" are today's orders where ``order_str.os_status = P and oh_amend =
  today``.
* "Old", "Today", and "Total" are open orders where ``sys-id = null``.
* In "Old", "Today", "Total", "Released", and "Packed" the top number is always
  the number of ``order_str`` orders, and the bottom number are units.
* To find out whether an order belongs to "Old" (<=yesterday) or "Today"
  (=today) check the ``order_hdr.oh_created`` field.
* Conversion is the amount of ``order_str`` orders which changed to
  ``order_str.os_status = P`` within the last 15 min. Chart is also drawn based
  on that (every 15 min the current "Conversion" is drawn).
* Update "To Complete" field based on most recent "Conversion" reading. "To
  Complete" shows the hours which it'll take to finish all left over open orders
  if worked at the current "Conversion".
* To find out what time ``order_str`` order was packed, join ``order_str`` with
  ``order_sscc`` and look for ``order_str.os_status = 'P' and oc_date_closed =
  'today' and max(order_sscc.oc_time_closed)``. This way I can trace back which
  ``order_str`` orders were packed between 7:00 and 7:15 even if I run the query
  at 10:00 only.

Units
=====
* Time fields are formatted in sec past midnight.

Tables
======
* order_hdr

  * Description

    Each order header represents one order sent from the host.
  * Primary keys

    * en_entity => company
    * pa_partner => customer
    * oh_order => order-no

  * Columns

    * oh_date => date order was created by host
    * oh_created => date order was created in our system
    * oh_status

      * '' => received or in progress
      * P => fully packed or short supplied, so it's closed

        Will automatically change to P once all assigned order_str orders have
        changed to P.
      * T => data transmitted to customer

* order_str

  * Description

    Each order header can contain multiple store orders. So customer1 can
    order 5 pieces for store1 and 4 pieces for store2 within the same order
    header.
  * Primary keys

    * en_entity => company
    * pa_partner => customer
    * oh_order => order-no
    * os_ship_to => is delivery destination
        Can be the same even if order is ultimately sent to CBD and Bondi.
    * os_store_loc => is CBD or Bondi, the actual store location who it's for.

  * Columns

    * os_sys_id
        Blank when received but set when order is started.
    * os_status

      * '' => received
      * I => as soon as SSCC is opened, status goes to I. So order was started
        and in progress.
      * P => packed full qty or force closed
      * T => data transmitted to customer

* order_line

  * Description

    Each store order can contain multiple order lines.
  * Primary keys

    * en_entity => company
    * pa_partner => customer
    * oh_order => order-no
    * os_store_loc
    * ol_line_seq

  * Columns

    * ol_status

      * '' => received
      * P => finished; if picked-qty is 0 but it's P then it was force closed
        order_line cannot be force closed but only the order_str.

    * ol_qty_ord => qty ordered
    * ol_qty_picked => qty picked

* order_sscc

  * Description

    Gives details which SSCCs (containers) are used for each store order.
  * Primary keys

    * en_entity => company
    * pa_partner => customer
    * oh_order => order-no
    * os_store_loc
    * oc_sscc

  * Columns

    * oc_date_created
    * oc_time_created
    * oc_date_closed
    * oc_time_closed

* order_pack

  * Description

    Gives details which lines are used for each SSCCs.
  * Primary keys

    * en_entity => company
    * pa_partner => customer
    * oh_order => order-no
    * os_store_loc
    * oc_sscc
    * ol_line_seq

Joining tables
==============
Link order if I need info from packs:

  order_hdr => order_str => order_sscc => order_pack => order_line

If I don't need pack details just do:

  order_hdr => order_str => order_line
