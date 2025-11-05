using System.Collections.Generic;

namespace DOTL.Core.Elements
{
    public static class ElementFactory
    {
        private static readonly Dictionary<string, Func<string, HtmlElement>> ElementCreators = new()
        {
            // Text elements
            { "txt", name => new DivElement(name) },
            { "h1", name => new Heading1Element(name) },
            { "h2", name => new Heading2Element(name) },
            { "h3", name => new Heading3Element(name) },
            { "p", name => new ParagraphElement(name) },
            { "span", name => new SpanElement(name) },
            { "div", name => new DivElement(name) },

            // Layout elements
            { "section", name => new TextElement(name, "section") },
            { "header", name => new TextElement(name, "header") },
            { "footer", name => new TextElement(name, "footer") },
            { "nav", name => new TextElement(name, "nav") },
            { "main", name => new TextElement(name, "main") },
            { "article", name => new TextElement(name, "article") },
            { "aside", name => new TextElement(name, "aside") },

            // Form elements
            { "form", name => new TextElement(name, "form") },
            { "input", name => new InputElement(name) },
            { "btn", name => new ButtonElement(name) },
            { "select", name => new TextElement(name, "select") },
            { "textarea", name => new TextElement(name, "textarea") },

            // Media elements
            { "img", name => new ImageElement(name) },
            { "video", name => new TextElement(name, "video") },
            { "audio", name => new TextElement(name, "audio") },

            // Interactive elements
            { "link", name => new LinkElement(name) },
            { "table", name => new TextElement(name, "table") },
            { "list", name => new TextElement(name, "ul") },
            { "ul", name => new TextElement(name, "ul") },
            { "ol", name => new TextElement(name, "ol") },
            { "li", name => new TextElement(name, "li") }
        };

        public static HtmlElement CreateElement(string elementType, string name)
        {
            if (ElementCreators.TryGetValue(elementType.ToLower(), out var creator))
            {
                return creator(name);
            }

            throw new ArgumentException($"Unknown element type: '{elementType}'. Available types: {string.Join(", ", ElementCreators.Keys.OrderBy(x => x))}");
        }

        public static IEnumerable<string> GetSupportedElementTypes()
        {
            return ElementCreators.Keys.OrderBy(x => x);
        }
    }
}