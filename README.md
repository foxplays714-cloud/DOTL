# DOTL - Domain-Oriented Text Language

A simple, intuitive language for creating websites with clean syntax that compiles to standard HTML5.

## Overview

DOTL (Domain-Oriented Text Language) provides a much simpler way to create websites compared to writing HTML directly. Instead of complex tags and attributes, DOTL uses a clear, readable syntax based on simple assignments.

### Basic Syntax

Instead of this HTML:
```html
<div class="welcome">
  <h1 id="title">Welcome to DOTL</h1>
  <p>This is a simple language for creating websites.</p>
</div>
```

You write this DOTL:
```dotl
txt.create = welcomeMessage
welcomeMessage.Class = "welcome"

h1.create = mainTitle
mainTitle.Text = "Welcome to DOTL"
mainTitle.Id = "title"

p.create = description
description.Text = "This is a simple language for creating websites."

welcomeMessage.add = mainTitle
welcomeMessage.add = description
```

## Features

- ✅ **Simple Syntax**: Easy-to-read assignment-based syntax
- ✅ **Element Types**: Support for all major HTML elements
- ✅ **Properties**: Full attribute support (Id, Class, Style, etc.)
- ✅ **Nesting**: Clean container/child relationships
- ✅ **Forms**: Complete form element support with validation
- ✅ **Media**: Images, video, and audio elements
- ✅ **CLI Tool**: Command-line compiler for .dotl files
- ✅ **Error Handling**: Clear error messages with line numbers

## Installation

### Prerequisites
- .NET 8.0 SDK or later

### Build from Source
```bash
git clone <repository-url>
cd DOTL
dotnet build
```

## Usage

### Command Line Interface

Compile a .dotl file to HTML:
```bash
dotnet run --project DOTL.CLI -- --input Examples/simple.dotl
```

Specify output file:
```bash
dotnet run --project DOTL.CLI -- --input Examples/layout.dotl --output mywebsite.html
```

Validate syntax only:
```bash
dotnet run --project DOTL.CLI -- --input Examples/form.dotl --validate
```

### Language Reference

#### Element Creation
```dotl
<elementType>.create = <variableName>
```

#### Property Assignment
```dotl
<variableName>.<property> = "<value>"
```

#### Container Relationships
```dotl
<container>.add = <childElement>
```

### Supported Element Types

#### Text Elements
- `txt.create` - Text containers (generates `<div>`)
- `h1.create` - Heading 1
- `h2.create` - Heading 2
- `h3.create` - Heading 3
- `p.create` - Paragraph
- `span.create` - Inline text

#### Layout Elements
- `div.create` - Division containers
- `section.create` - Semantic sections
- `header.create` - Page header
- `footer.create` - Page footer
- `nav.create` - Navigation
- `main.create` - Main content area
- `article.create` - Article content
- `aside.create` - Sidebar content

#### Form Elements
- `form.create` - Form containers
- `input.create` - Input fields
- `btn.create` - Buttons
- `select.create` - Dropdown selects
- `textarea.create` - Text areas

#### Media Elements
- `img.create` - Images
- `video.create` - Video players
- `audio.create` - Audio players

#### Interactive Elements
- `link.create` - Hyperlinks
- `table.create` - Tables
- `list.create` - Lists (generates `<ul>`)
- `ul.create` - Unordered lists
- `ol.create` - Ordered lists
- `li.create` - List items

### Common Properties

#### All Elements
- `Id = "string"` - HTML id attribute
- `Class = "string"` - CSS class names
- `Style = "css"` - Inline CSS styles

#### Text Properties
- `Text = "content"` - Inner text content
- `Html = "content"` - Inner HTML content

#### Input Properties
- `Type = "text|email|password|number|..."` - Input type
- `Placeholder = "text"` - Placeholder text
- `Value = "value"` - Default value
- `Required = "true|false"` - Required field
- `Name = "string"` - Form field name

#### Link Properties
- `Href = "url"` - Link destination
- `Target = "_blank|_self|..."` - Link target

#### Image Properties
- `Src = "path"` - Image source
- `Alt = "text"` - Alt text
- `Width = "pixels"` - Width
- `Height = "pixels"` - Height

#### Form Properties
- `Action = "url"` - Form submission URL
- `Method = "GET|POST"` - HTTP method

## Examples

### Simple Website
```dotl
# Examples/simple.dotl
txt.create = welcomeMessage
welcomeMessage.Text = "Hello, World!"
welcomeMessage.Class = "welcome"

h1.create = mainTitle
mainTitle.Text = "Welcome to DOTL"
mainTitle.Id = "title"

p.create = description
description.Text = "DOTL is a simple language for creating websites."

welcomeMessage.add = mainTitle
welcomeMessage.add = description
```

### Contact Form
```dotl
# Examples/form.dotl
form.create = contactForm
contactForm.Action = "/submit"
contactForm.Method = "POST"

input.create = nameField
nameField.Type = "text"
nameField.Placeholder = "Enter your name"
nameField.Required = "true"

input.create = emailField
emailField.Type = "email"
emailField.Placeholder = "Enter your email"
emailField.Required = "true"

btn.create = submitButton
submitButton.Text = "Submit"
submitButton.Type = "submit"

contactForm.add = nameField
contactForm.add = emailField
contactForm.add = submitButton
```

### Complete Layout
```dotl
# Examples/layout.dotl
div.create = page
page.Class = "container"

header.create = siteHeader
siteHeader.Class = "header"

h1.create = siteTitle
siteTitle.Text = "My Awesome Website"

nav.create = mainNav
mainNav.Class = "navigation"

link.create = homeLink
homeLink.Text = "Home"
homeLink.Href = "/"
homeLink.Class = "nav-link"

link.create = aboutLink
aboutLink.Text = "About"
aboutLink.Href = "/about"

mainNav.add = homeLink
mainNav.add = aboutLink

siteHeader.add = siteTitle
siteHeader.add = mainNav
page.add = siteHeader
```

## Project Structure

```
DOTL/
├── DOTL.sln                    # Solution file
├── DOTL.Core/                   # Core language implementation
│   ├── Parser/
│   │   ├── Lexer.cs            # Tokenizes .dotl files
│   │   ├── Parser.cs           # Parses tokens to AST
│   │   └── AST/                # AST node definitions
│   ├── Elements/
│   │   ├── HtmlElement.cs      # Base element class
│   │   ├── TextElement.cs      # Text-based elements
│   │   ├── InputElement.cs     # Form elements
│   │   ├── MediaElement.cs     # Media elements
│   │   └── ElementFactory.cs   # Element creation factory
│   ├── Generator/
│   │   └── HtmlGenerator.cs    # Converts AST to HTML
│   └── Runtime/
│       ├── ElementRegistry.cs  # Manages created elements
│       └── ErrorHandler.cs     # Error handling utilities
├── DOTL.CLI/
│   └── Program.cs              # Command-line interface
└── Examples/
    ├── simple.dotl             # Basic example
    ├── form.dotl               # Form example
    └── layout.dotl             # Complete layout example
```

## Error Handling

DOTL provides clear error messages with line numbers:

```
Error: Unknown element type 'txtx' at line 5, column 1
Code: UNKNOWN_ELEMENT
Line 5: txtx.create = exampleName
        ^
Available types: txt, h1, h2, h3, p, div, section, header, footer, nav, main, article, aside, form, input, btn, select, textarea, img, video, audio, link, table, list, ul, ol, li
```

## Contributing

This is a demonstration project showcasing how to build a domain-specific language in C#. The implementation includes:

- Lexer and parser for custom syntax
- Abstract Syntax Tree (AST) generation
- HTML generation from AST
- Command-line tool interface
- Comprehensive error handling

## License

MIT License - feel free to use this as a learning example or starting point for your own DSL projects.
