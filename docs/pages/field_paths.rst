.. _field_paths:

===========
Field Paths
===========

Field paths are a special syntax for describing document positions within the 0-Meter configuration files.

JSON fields can be contained either in lists or in objects.  A field path might look like this:

`responses[0.codes[1`

The use of `[` signifies an array, and the use of `.` signifies an object.  Here's the JSON message this would parse:

{responses: [{codes: [0, 1]}]}

The above field path would return the value '1' from the response message.
