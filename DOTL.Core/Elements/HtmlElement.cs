using System.Collections.Generic;
using System.Text;

namespace DOTL.Core.Elements
{
    public abstract class HtmlElement
    {
        public string Name { get; }
        public string HtmlTag { get; }
        public Dictionary<string, string> Attributes { get; }
        public List<HtmlElement> Children { get; }
        public string? InnerText { get; set; }
        public string? InnerHtml { get; set; }

        protected HtmlElement(string name, string htmlTag)
        {
            Name = name;
            HtmlTag = htmlTag;
            Attributes = new Dictionary<string, string>();
            Children = new List<HtmlElement>();
        }

        public virtual void SetProperty(string propertyName, string value)
        {
            switch (propertyName.ToLower())
            {
                case "id":
                    Attributes["id"] = value;
                    break;
                case "class":
                    Attributes["class"] = value;
                    break;
                case "style":
                    Attributes["style"] = value;
                    break;
                case "text":
                    InnerText = value;
                    break;
                case "html":
                    InnerHtml = value;
                    break;
                default:
                    SetPropertyCore(propertyName, value);
                    break;
            }
        }

        protected virtual void SetPropertyCore(string propertyName, string value)
        {
            // Allow derived classes to handle specific properties
            Attributes[propertyName.ToLower()] = value;
        }

        public virtual string GenerateHtml(int indentLevel = 0)
        {
            var indent = new string(' ', indentLevel * 2);
            var builder = new StringBuilder();

            builder.Append($"{indent}<{HtmlTag}");

            // Add attributes
            foreach (var attr in Attributes)
            {
                builder.Append($" {attr.Key}=\"{EscapeHtml(attr.Value)}\"");
            }

            if (HasContent())
            {
                builder.AppendLine(">");

                // Add inner text if present
                if (!string.IsNullOrEmpty(InnerText))
                {
                    builder.AppendLine($"{new string(' ', (indentLevel + 1) * 2)}{EscapeHtml(InnerText)}");
                }

                // Add inner HTML if present
                if (!string.IsNullOrEmpty(InnerHtml))
                {
                    var innerLines = InnerHtml.Split('\n');
                    foreach (var line in innerLines)
                    {
                        builder.AppendLine($"{new string(' ', (indentLevel + 1) * 2)}{line}");
                    }
                }

                // Add children
                foreach (var child in Children)
                {
                    builder.AppendLine(child.GenerateHtml(indentLevel + 1));
                }

                builder.AppendLine($"{indent}</{HtmlTag}>");
            }
            else
            {
                builder.AppendLine(" />");
            }

            return builder.ToString();
        }

        private bool HasContent()
        {
            return !string.IsNullOrEmpty(InnerText) ||
                   !string.IsNullOrEmpty(InnerHtml) ||
                   Children.Count > 0;
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

        public override string ToString()
        {
            return $"{HtmlTag} element '{Name}'";
        }
    }
}