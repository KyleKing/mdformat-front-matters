YAML double-quoted strings preserved by default
.
---
title: "My Post"
author: "Jane Doe"
unquoted: value
---

Content.
.
---
title: "My Post"
author: "Jane Doe"
unquoted: value
---

Content.
.

YAML single-quoted strings preserved by default
.
---
title: 'My Post'
special: 'value'
---

Content.
.
---
title: 'My Post'
special: 'value'
---

Content.
.

YAML necessary quotes preserved under normalize (colon, bool-like, empty)
{"normalize_front_matter": "minimal"}
.
---
title: "value: with colon"
bool_str: "true"
empty: ""
---

Content.
.
---
title: 'value: with colon'
bool_str: 'true'
empty: ''
---

Content.
.

YAML double-quoted strings stripped under normalize
{"normalize_front_matter": "minimal"}
.
---
title: "My Post"
author: "Jane Doe"
unquoted: value
---

Content.
.
---
title: My Post
author: Jane Doe
unquoted: value
---

Content.
.

YAML single-quoted strings stripped under normalize
{"normalize_front_matter": "minimal"}
.
---
title: 'My Post'
special: 'value'
---

Content.
.
---
title: My Post
special: value
---

Content.
.

YAML block literal style preserved under normalize
{"normalize_front_matter": "minimal"}
.
---
description: |
  line one
  line two
title: Test
---

Content.
.
---
description: |
  line one
  line two
title: Test
---

Content.
.

YAML block folded style preserved under normalize
{"normalize_front_matter": "minimal"}
.
---
description: >
  wrapped text
title: Test
---

Content.
.
---
description: >
  wrapped text
title: Test
---

Content.
.
