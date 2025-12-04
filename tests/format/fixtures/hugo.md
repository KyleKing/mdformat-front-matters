Parameters (yaml)
.
---
date: 2024-02-02T04:14:54-08:00
draft:   false
params:
  author: 'John Smith'
title:    "Example"
weight: 10
---
.
---
date: 2024-02-02T04:14:54-08:00
draft: false
params:
  author: John Smith
title: Example
weight: 10
---
.

Parameters (toml)
.
+++
date =2024-02-02T04:14:54-08:00
draft= false
title = "Example"
weight = 10
[params]
  author = 'John Smith'
+++
.
+++
date = 2024-02-02T04:14:54-08:00
draft = false
title = "Example"
weight = 10
[params]
author = "John Smith"
+++
.

Parameters (json)
.
{
   "date":"2024-02-02T04:14:54-08:00",
   "draft": false,
   "params": {      "author": "John Smith"
   },
"title": "Example",
   "weight": 10
}
.
{
    "date": "2024-02-02T04:14:54-08:00",
    "draft": false,
    "params": {
        "author": "John Smith"
    },
    "title": "Example",
    "weight": 10
}
.
