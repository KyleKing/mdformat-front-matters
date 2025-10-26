a test
.
This is the input Markdown test,
then below add the expected output.
.
This is the input Markdown test,
then below add the expected output.
.

another test
.
Some *markdown*

- a
- b
* c
.
Some *markdown*

- a
- b

* c
.

Test yaml header
.
---
some: yaml
---
# Now some markdown
And some more.
.
---
some: yaml
---

# Now some markdown

And some more.
.

Test yaml reformat
.
---
some: yaml

---
# Now some markdown
And some more.
.
---
some: yaml
---

# Now some markdown

And some more.
.

CommonMark v0.29 spec example 66
.
---
Foo
---
Bar
---
Baz
.
---
Foo
---

## Bar

Baz
.

CommonMark v0.29 spec example 68
.
---
---
.
---
null
---
.

YAML parse error
.
---
] This is a YAML parse error


Dont format.
---
.
---
] This is a YAML parse error


Dont format.
---
.

Test long line endings
.
---
somethingthatis: reallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallylong
---
.
---
somethingthatis: reallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallyreallylong
---
.

YAML parse error duplicate keys
.
---
] This is a YAML parse error
stuff: stuff
stuff: stuff
---
.
---
] This is a YAML parse error
stuff: stuff
stuff: stuff
---
.

TODO: Format Hugo TOML front matter example
.
+++
title = "Example"
date = 2024-02-02T04:14:54-08:00
draft = false
weight = 10
[params]
author = "John Smith"
+++
# Example Headline

Hugo uses TOML front matter with nested tables.
.
+++
title = "Example"
date = 2024-02-02T04:14:54-08:00
draft = false
weight = 10

[params]
author = "John Smith"
+++

# Example Headline

Hugo uses TOML front matter with nested tables.
.

TODO: Format Hugo YAML front matter example
.
---
title: Example
date: 2024-02-02T04:14:54-08:00
draft: false
weight: 10
params:
  author: John Smith
---
# Example Headline

Hugo uses YAML front matter with nested maps.
.
---
title: Example
date: 2024-02-02T04:14:54-08:00
draft: false
weight: 10
params:
  author: John Smith
---

# Example Headline

Hugo uses YAML front matter with nested maps.
.

TODO: Format Hugo JSON front matter example
.
{
"title": "Example",
"date": "2024-02-02T04:14:54-08:00",
"draft": false,
"weight": 10,
"params": {"author": "John Smith"}
}
# Example Headline

Hugo uses JSON front matter with nested objects.
.
{
  "title": "Example",
  "date": "2024-02-02T04:14:54-08:00",
  "draft": false,
  "weight": 10,
  "params": {
    "author": "John Smith"
  }
}

# Example Headline

Hugo uses JSON front matter with nested objects.
.

Deeply nested YAML structure
.
---
database:
  connections:
    primary:
      host: localhost
      port: 5432
      credentials:
        username: admin
        password: secret
    secondary:
      host: backup.example.com
      port: 5432
  settings:
    pool_size: 10
    timeout: 30
tags:
  - nested
  - arrays
  - testing
metadata:
  created_by:
    name: John Doe
    email: john@example.com
---
# Content
.
---
database:
  connections:
    primary:
      host: localhost
      port: 5432
      credentials:
        username: admin
        password: secret
    secondary:
      host: backup.example.com
      port: 5432
  settings:
    pool_size: 10
    timeout: 30
tags: [nested, arrays, testing]
metadata:
  created_by:
    name: John Doe
    email: john@example.com
---

# Content
.

YAML with complex arrays and objects
.
---
features:
  - name: authentication
    enabled: true
    config:
      providers:
        - oauth
        - saml
      timeout: 3600
  - name: logging
    enabled: false
    config:
      level: debug
      handlers:
        - console
        - file
matrix:
  - [1, 2, 3]
  - [4, 5, 6]
  - [7, 8, 9]
---
# Content
.
---
features:
  - name: authentication
    enabled: true
    config:
      providers: [oauth, saml]
      timeout: 3600
  - name: logging
    enabled: false
    config:
      level: debug
      handlers: [console, file]
matrix:
  - [1, 2, 3]
  - [4, 5, 6]
  - [7, 8, 9]
---

# Content
.

TOML with deeply nested tables
.
+++
[server]
host = "example.com"
port = 8080

[server.ssl]
enabled = true
cert = "/path/to/cert"

[server.ssl.options]
min_version = "TLSv1.2"
ciphers = ["ECDHE-RSA-AES256-GCM-SHA384"]

[database]
driver = "postgres"

[database.primary]
host = "db1.example.com"
port = 5432

[database.primary.pool]
min_connections = 5
max_connections = 20

[[logging.handlers]]
type = "file"
path = "/var/log/app.log"

[[logging.handlers]]
type = "console"
level = "debug"
+++
# Content
.
+++
[server]
host = "example.com"
port = 8080

[server.ssl]
enabled = true
cert = "/path/to/cert"

[server.ssl.options]
min_version = "TLSv1.2"
ciphers = [
    "ECDHE-RSA-AES256-GCM-SHA384",
]

[database]
driver = "postgres"

[database.primary]
host = "db1.example.com"
port = 5432

[database.primary.pool]
min_connections = 5
max_connections = 20

[logging]
handlers = [
    { type = "file", path = "/var/log/app.log" },
    { type = "console", level = "debug" },
]
+++

# Content
.

Malformed - Missing closing YAML delimiter
.
---
title: Test
description: This is missing a closing delimiter

# Content starts without closing
.
______________________________________________________________________

title: Test
description: This is missing a closing delimiter

# Content starts without closing
.

Malformed - Invalid YAML indentation
.
---
parent:
child: wrong_indent
  another: also_wrong
---
# Content
.
---
parent:
child: wrong_indent
  another: also_wrong
---

# Content
.

Malformed - Mixed tabs and spaces in YAML
.
---
title: Test
	description: Has tab character
  value: Has spaces
---
# Content
.
---
title: Test
	description: Has tab character
  value: Has spaces
---

# Content
.

Malformed - Invalid TOML syntax
.
+++
title = "Missing quote
description = "Valid"
+++
# Content
.
+++
title = "Missing quote
description = "Valid"
+++

# Content
.

Malformed - YAML with invalid anchor reference
.
---
base: &anchor
  value: test
derived: *nonexistent
---
# Content
.
---
base: &anchor
  value: test
derived: *nonexistent
---

# Content
.

Malformed - JSON with trailing comma
.
{
  "title": "Test",
  "description": "Invalid JSON",
}
# Content
.
{
"title": "Test",
"description": "Invalid JSON",
}

# Content
.

Malformed - Empty front matter block
.
---
---
# Content
.
---
null
---

# Content
.

Malformed - Front matter with unicode and special characters
.
---
title: Test with émojis 🎉 and spëcial chars
description: "Quotes: \"nested\" 'single'"
path: C:\Windows\Path\With\Backslashes
regex: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
---
# Content
.
---
title: Test with émojis 🎉 and spëcial chars
description: "Quotes: \"nested\" 'single'"
path: C:\Windows\Path\With\Backslashes
regex: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
---

# Content
.

Very large YAML front matter
.
---
large_config:
  setting_001: value_001
  setting_002: value_002
  setting_003: value_003
  setting_004: value_004
  setting_005: value_005
  setting_006: value_006
  setting_007: value_007
  setting_008: value_008
  setting_009: value_009
  setting_010: value_010
  setting_011: value_011
  setting_012: value_012
  setting_013: value_013
  setting_014: value_014
  setting_015: value_015
  setting_016: value_016
  setting_017: value_017
  setting_018: value_018
  setting_019: value_019
  setting_020: value_020
  setting_021: value_021
  setting_022: value_022
  setting_023: value_023
  setting_024: value_024
  setting_025: value_025
  setting_026: value_026
  setting_027: value_027
  setting_028: value_028
  setting_029: value_029
  setting_030: value_030
large_array:
  - item_001
  - item_002
  - item_003
  - item_004
  - item_005
  - item_006
  - item_007
  - item_008
  - item_009
  - item_010
  - item_011
  - item_012
  - item_013
  - item_014
  - item_015
  - item_016
  - item_017
  - item_018
  - item_019
  - item_020
large_text: This is a very long text value that spans multiple words and could potentially cause line wrapping issues if the formatter doesnt handle it correctly. It contains many characters and should be preserved exactly as written without modification to its content or structure.
---
# Content
.
---
large_config:
  setting_001: value_001
  setting_002: value_002
  setting_003: value_003
  setting_004: value_004
  setting_005: value_005
  setting_006: value_006
  setting_007: value_007
  setting_008: value_008
  setting_009: value_009
  setting_010: value_010
  setting_011: value_011
  setting_012: value_012
  setting_013: value_013
  setting_014: value_014
  setting_015: value_015
  setting_016: value_016
  setting_017: value_017
  setting_018: value_018
  setting_019: value_019
  setting_020: value_020
  setting_021: value_021
  setting_022: value_022
  setting_023: value_023
  setting_024: value_024
  setting_025: value_025
  setting_026: value_026
  setting_027: value_027
  setting_028: value_028
  setting_029: value_029
  setting_030: value_030
large_array:
  - item_001
  - item_002
  - item_003
  - item_004
  - item_005
  - item_006
  - item_007
  - item_008
  - item_009
  - item_010
  - item_011
  - item_012
  - item_013
  - item_014
  - item_015
  - item_016
  - item_017
  - item_018
  - item_019
  - item_020
large_text: This is a very long text value that spans multiple words and could potentially
  cause line wrapping issues if the formatter doesnt handle it correctly. It contains
  many characters and should be preserved exactly as written without modification
  to its content or structure.
---

# Content
.

Very large TOML front matter with arrays of tables
.
+++
version = "1.0.0"
description = "Large configuration file for testing"

[[services]]
name = "service_001"
enabled = true
port = 8001

[[services]]
name = "service_002"
enabled = true
port = 8002

[[services]]
name = "service_003"
enabled = false
port = 8003

[[services]]
name = "service_004"
enabled = true
port = 8004

[[services]]
name = "service_005"
enabled = true
port = 8005

[[servers]]
hostname = "server001.example.com"
ip = "192.168.1.1"
datacenter = "us-east-1"

[[servers]]
hostname = "server002.example.com"
ip = "192.168.1.2"
datacenter = "us-east-1"

[[servers]]
hostname = "server003.example.com"
ip = "192.168.1.3"
datacenter = "us-west-1"

[[servers]]
hostname = "server004.example.com"
ip = "192.168.1.4"
datacenter = "us-west-1"

[[servers]]
hostname = "server005.example.com"
ip = "192.168.1.5"
datacenter = "eu-central-1"

[metadata]
created = 2024-01-01T00:00:00Z
updated = 2024-12-31T23:59:59Z
author = "System Administrator"
tags = ["production", "critical", "monitored"]
+++
# Content
.
+++
version = "1.0.0"
description = "Large configuration file for testing"
services = [
    { name = "service_001", enabled = true, port = 8001 },
    { name = "service_002", enabled = true, port = 8002 },
    { name = "service_003", enabled = false, port = 8003 },
    { name = "service_004", enabled = true, port = 8004 },
    { name = "service_005", enabled = true, port = 8005 },
]
servers = [
    { hostname = "server001.example.com", ip = "192.168.1.1", datacenter = "us-east-1" },
    { hostname = "server002.example.com", ip = "192.168.1.2", datacenter = "us-east-1" },
    { hostname = "server003.example.com", ip = "192.168.1.3", datacenter = "us-west-1" },
    { hostname = "server004.example.com", ip = "192.168.1.4", datacenter = "us-west-1" },
    { hostname = "server005.example.com", ip = "192.168.1.5", datacenter = "eu-central-1" },
]

[metadata]
created = 2024-01-01T00:00:00+00:00
updated = 2024-12-31T23:59:59+00:00
author = "System Administrator"
tags = [
    "production",
    "critical",
    "monitored",
]
+++

# Content
.

YAML with multiline strings
.
---
description: |
  This is a multiline string
  that spans multiple lines
  and preserves formatting
script: >
  This is a folded string
  that will be concatenated
  into a single line
literal: |-
  Line one
  Line two
  Line three
---
# Content
.
---
description: |
  This is a multiline string
  that spans multiple lines
  and preserves formatting
script: >
  This is a folded string
  that will be concatenated
  into a single line
literal: |-
  Line one
  Line two
  Line three
---

# Content
.
