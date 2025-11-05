namespace DOTL.Core.Elements
{
    public class ImageElement : HtmlElement
    {
        public ImageElement(string name) : base(name, "img")
        {
            // Images are self-closing by default
        }

        protected override void SetPropertyCore(string propertyName, string value)
        {
            switch (propertyName.ToLower())
            {
                case "src":
                    Attributes["src"] = value;
                    break;
                case "alt":
                    Attributes["alt"] = value;
                    break;
                case "width":
                    Attributes["width"] = value;
                    break;
                case "height":
                    Attributes["height"] = value;
                    break;
                default:
                    base.SetPropertyCore(propertyName, value);
                    break;
            }
        }

        public override string GenerateHtml(int indentLevel = 0)
        {
            var indent = new string(' ', indentLevel * 2);
            var builder = new System.Text.StringBuilder();

            builder.Append($"{indent}<{HtmlTag}");

            // Add attributes
            foreach (var attr in Attributes)
            {
                if (!string.IsNullOrEmpty(attr.Value))
                {
                    builder.Append($" {attr.Key}=\"{EscapeHtml(attr.Value)}\"");
                }
            }

            builder.AppendLine(" />");

            return builder.ToString();
        }

        private string EscapeHtml(string input)
        {
            if (string.IsNullOrEmpty(input)) return input;

            return input
                .Replace("&", "&amp;")
                .Replace("<", "&lt;")
                .Replace(">", "&gt;")
                .Replace("\"", "&quot;")
                .Replace("'", "&#39;");
        }
    }

    public class LinkElement : HtmlElement
    {
        public LinkElement(string name) : base(name, "a")
        {
        }

        protected override void SetPropertyCore(string propertyName, string value)
        {
            switch (propertyName.ToLower())
            {
                case "href":
                    Attributes["href"] = value;
                    break;
                case "target":
                    Attributes["target"] = value;
                    break;
                default:
                    base.SetPropertyCore(propertyName, value);
                    break;
            }
        }
    }
}