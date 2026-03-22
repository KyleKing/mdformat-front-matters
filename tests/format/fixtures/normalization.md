YAML null tilde normalized to null
{"normalize_front_matter": "minimal"}
.
---
key: ~
nested:
  value: ~
---

Content.
.
---
key: null
nested:
  value: null
---

Content.
.

YAML implicit null normalized to explicit null
{"normalize_front_matter": "minimal"}
.
---
key:
title: Test
---

Content.
.
---
key: null
title: Test
---

Content.
.

YAML null unchanged under none
.
---
key: ~
---

Content.
.
---
key:
---

Content.
.

YAML boolean case normalized under minimal
{"normalize_front_matter": "minimal"}
.
---
draft: True
published: False
archived: TRUE
---

Content.
.
---
draft: true
published: false
archived: true
---

Content.
.

YAML 1.1 unquoted yes/no converted under 1.2
{"normalize_front_matter": "1.2"}
.
---
draft: yes
published: no
---

Content.
.
---
draft: true
published: false
---

Content.
.

YAML 1.1 unquoted on/off converted under 1.2
{"normalize_front_matter": "1.2"}
.
---
feature: on
legacy: off
---

Content.
.
---
feature: true
legacy: false
---

Content.
.

YAML 1.1 capitalised variants converted under 1.2
{"normalize_front_matter": "1.2"}
.
---
a: Yes
b: No
c: ON
d: OFF
e: YES
f: NO
---

Content.
.
---
a: true
b: false
c: true
d: false
e: true
f: false
---

Content.
.

YAML 1.1 quoted yes preserved as string under 1.2
{"normalize_front_matter": "1.2"}
.
---
label: "yes"
answer: 'no'
status: "on"
---

Content.
.
---
label: yes
answer: no
status: on
---

Content.
.

YAML 1.1 booleans unchanged under minimal
{"normalize_front_matter": "minimal"}
.
---
draft: yes
published: no
---

Content.
.
---
draft: yes
published: no
---

Content.
.

YAML 1.1 booleans unchanged under none
.
---
draft: yes
published: no
---

Content.
.
---
draft: yes
published: no
---

Content.
.

YAML 1.2 mode includes minimal normalizations
{"normalize_front_matter": "1.2"}
.
---
title: "My Post"
draft: yes
null_val: ~
---

Content.
.
---
title: My Post
draft: true
null_val: null
---

Content.
.
