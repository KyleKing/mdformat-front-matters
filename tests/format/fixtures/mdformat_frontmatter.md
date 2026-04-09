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

YAML non-standard linewrap
{".wrap": 40}
.
---
somethingthatis: notsoreallyreallyreallylong
---
This text is wrapped, too, since the wrap option applies to the entire document.
.
---
somethingthatis: 
  notsoreallyreallyreallylong
---

This text is wrapped, too, since the
wrap option applies to the entire
document.
.
YAML non-standard linewrap but regular wrap
{"wrap_front_matter": 40}
.
---
somethingthatis: notsoreallyreallyreallylong
---
This text is not wrapped despite being more than forty characters.
.
---
somethingthatis: 
  notsoreallyreallyreallylong
---

This text is not wrapped despite being more than forty characters.
.
YAML linewrap only in content, not frontmatter
{".wrap": 40, "wrap_front_matter": 0}
.
---
somethingthatis: reallyreallyreallyreallylong
---
This text is being wrapped since the wrap option is used.
.
---
somethingthatis: reallyreallyreallyreallylong
---

This text is being wrapped since the
wrap option is used.
.
