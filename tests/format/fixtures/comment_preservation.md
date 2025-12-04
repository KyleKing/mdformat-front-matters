YAML comments at end of line
.
---
# Main title comment
title: My Document
# Author comment
author: John Doe
tags:
  - python  # programming language
  - yaml  # configuration format
---

# Content
.
---
# Main title comment
title: My Document
# Author comment
author: John Doe
tags:
  - python  # programming language
  - yaml  # configuration format
---

# Content
.

YAML comments on separate lines
.
---
# This is a configuration file
# for a blog post

title: Blog Post
description: A sample post

# Publication metadata
published: true
date: 2023-01-01
---

# Blog Content
.
---
# This is a configuration file
# for a blog post

title: Blog Post
description: A sample post

# Publication metadata
published: true
date: 2023-01-01
---

# Blog Content
.

YAML mixed comments and values
.
---
# Page configuration
layout: post  # Use post layout
draft: false  # Ready for publication

# SEO fields
meta:
  keywords: test  # Search keywords
  robots: index  # Allow indexing
---

Content here.
.
---
# Page configuration
layout: post  # Use post layout
draft: false  # Ready for publication

# SEO fields
meta:
  keywords: test  # Search keywords
  robots: index  # Allow indexing
---

Content here.
.

YAML comments with special characters
.
---
# TODO: Update this section
title: Test # This needs review!
# FIXME: Check the URL
url: /test  # Should this be /tests?
---

# Markdown
.
---
# TODO: Update this section
title: Test # This needs review!
# FIXME: Check the URL
url: /test  # Should this be /tests?
---

# Markdown
.

YAML comments in nested structures
.
---
# Top level comment
config:
  # Nested comment
  option1: value1  # inline comment
  option2: value2
  nested:
    # Deep comment
    deep_key: deep_value
---

Content.
.
---
# Top level comment
config:
  # Nested comment
  option1: value1  # inline comment
  option2: value2
  nested:
    # Deep comment
    deep_key: deep_value
---

Content.
.

YAML empty front matter with comments
.
---
# This is an empty configuration
# Just comments, no values
---

# Heading
.
---
# This is an empty configuration
# Just comments, no values
---

# Heading
.

YAML multiline string with hash
.
---
description: |
  This is a multiline description
  # This is not a comment, it's content
  It continues here
title: Test
---

# Content
.
---
description: |
  This is a multiline description
  # This is not a comment, it's content
  It continues here
title: Test
---

# Content
.
