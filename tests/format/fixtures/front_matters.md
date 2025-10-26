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
