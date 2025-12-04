YAML front matter with sort
{"sort_front_matter": true}
.
---
z_key: last
a_key: first
m_key: middle
nested:
  z_sub: last
  a_sub: first
---

Content here.
.
---
a_key: first
m_key: middle
nested:
  a_sub: first
  z_sub: last
z_key: last
---

Content here.
.

TOML front matter with sort
{"sort_front_matter": true}
.
+++
z_key = "last"
a_key = "first"
m_key = "middle"
+++

Content here.
.
+++
a_key = "first"
m_key = "middle"
z_key = "last"
+++

Content here.
.

JSON front matter with sort
{"sort_front_matter": true}
.
{
"z_key": "last",
"a_key": "first",
"m_key": "middle"
}

Content here.
.
{
    "a_key": "first",
    "m_key": "middle",
    "z_key": "last"
}

Content here.
.

YAML comments preserved with sort
{"sort_front_matter": true}
.
---
# Configuration section
z_key: last  # This should move
a_key: first  # This should be first
# Middle section comment
m_key: middle
nested:
  z_sub: last  # nested comment
  a_sub: first
---

Content here.
.
---
# Configuration section
a_key: first  # This should be first
# Middle section comment
m_key: middle
nested:
  a_sub: first
  z_sub: last  # nested comment
z_key: last  # This should move
---

Content here.
.

YAML standalone block comments edge case
{"sort_front_matter": true}
.
---
z_field: value1
# This comment is before m_field
m_field: value2
a_field: value3
---

Content.
.
---
a_field: value3
m_field: value2
z_field: value1
# This comment is before m_field
---

Content.
.
