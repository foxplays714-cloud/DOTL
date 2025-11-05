namespace DOTL.Core.Elements
{
    public class TextElement : HtmlElement
    {
        public TextElement(string name, string htmlTag) : base(name, htmlTag)
        {
        }
    }

    public class Heading1Element : TextElement
    {
        public Heading1Element(string name) : base(name, "h1") { }
    }

    public class Heading2Element : TextElement
    {
        public Heading2Element(string name) : base(name, "h2") { }
    }

    public class Heading3Element : TextElement
    {
        public Heading3Element(string name) : base(name, "h3") { }
    }

    public class ParagraphElement : TextElement
    {
        public ParagraphElement(string name) : base(name, "p") { }
    }

    public class SpanElement : TextElement
    {
        public SpanElement(string name) : base(name, "span") { }
    }

    public class DivElement : TextElement
    {
        public DivElement(string name) : base(name, "div") { }
    }
}