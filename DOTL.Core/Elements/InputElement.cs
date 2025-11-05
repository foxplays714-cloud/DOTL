namespace DOTL.Core.Elements
{
    public class InputElement : HtmlElement
    {
        public InputElement(string name) : base(name, "input")
        {
            // Input elements are self-closing by default
        }

        protected override void SetPropertyCore(string propertyName, string value)
        {
            switch (propertyName.ToLower())
            {
                case "type":
                    Attributes["type"] = value;
                    break;
                case "placeholder":
                    Attributes["placeholder"] = value;
                    break;
                case "value":
                    Attributes["value"] = value;
                    break;
                case "required":
                    Attributes["required"] = value.ToLower() == "true" ? "required" : "";
                    break;
                case "name":
                    Attributes["name"] = value;
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
                else
                {
                    builder.Append($" {attr.Key}");
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

    public class ButtonElement : HtmlElement
    {
        public ButtonElement(string name) : base(name, "button")
        {
        }

        protected override void SetPropertyCore(string propertyName, string value)
        {
            switch (propertyName.ToLower())
            {
                case "type":
                    Attributes["type"] = value;
                    break;
                case "value":
                    Attributes["value"] = value;
                    break;
                default:
                    base.SetPropertyCore(propertyName, value);
                    break;
            }
        }
    }
}