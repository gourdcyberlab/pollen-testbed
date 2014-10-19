## field
- members:
  - name
    - (parameter)
  - default
    - (any2i(parameter))
  - fmt
    - (parameter or "H")
    - used for struct
  - sz
    - used for struct
  - owners
    - (list)

- different formats
  - internal
  - human
  - machine
  - count
  - repr
  - internal is the common format. translating from one to another requires
    going through internal first.

- methods
  - several `*2*`
    - each accepts self, packet, and `x`.
    - seems to convert x between different formats
  - `addfield`
    - accepts self, packet, `s`, and `val`
    - assuming `s` is string version of a packet, and val is a value for this
      field to be added to string
    - returns string + machine version of x
  - `getfield`
    - accepts self, packet, and `s` (assuming packet string again)
    - returns an internal value made from front `sz` of string, and remainder

// It looks like the "options" field in an IP packet is supposed to hold packets
// I'm not sure what that means now...

- methods
  - several `*2*`
    - each accepts self, packet, and `x`.
    - seems to convert x between different formats
  - `addfield`
    - accepts self, packet, `s`, and `val`
    - assuming `s` is string version of a packet, and val is a value for this
      field to be added to string
  - `getfield`
    - accepts self, packet, and `s` (assuming packet string again)
    - returns an internal value from back of string, and rest of string
  - `copy`/`do_copy`
  - `repr`
  - `randval`
