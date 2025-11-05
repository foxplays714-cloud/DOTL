using System.Text;

namespace DOTL.Core.Runtime
{
    public class DotlException : Exception
    {
        public int Line { get; }
        public int Column { get; }
        public string ErrorCode { get; }

        public DotlException(string message, int line, int column, string errorCode = "DOTL_ERROR")
            : base($"{message} at line {line}, column {column}")
        {
            Line = line;
            Column = column;
            ErrorCode = errorCode;
        }

        public DotlException(string message, Exception innerException, int line, int column, string errorCode = "DOTL_ERROR")
            : base($"{message} at line {line}, column {column}", innerException)
        {
            Line = line;
            Column = column;
            ErrorCode = errorCode;
        }
    }

    public class ErrorHandler
    {
        public static DotlException CreateSyntaxError(string expected, string actual, int line, int column)
        {
            return new DotlException($"Syntax error: Expected {expected} but found '{actual}'", line, column, "SYNTAX_ERROR");
        }

        public static DotlException CreateUnknownElementError(string elementType, int line, int column)
        {
            var message = $"Unknown element type '{elementType}'. Available types: txt, h1, h2, h3, p, div, section, header, footer, nav, main, article, aside, form, input, btn, select, textarea, img, video, audio, link, table, list, ul, ol, li";
            return new DotlException(message, line, column, "UNKNOWN_ELEMENT");
        }

        public static DotlException CreateUnknownPropertyError(string propertyName, string elementType, int line, int column)
        {
            var message = $"Unknown property '{propertyName}' for element type '{elementType}'";
            return new DotlException(message, line, column, "UNKNOWN_PROPERTY");
        }

        public static DotlException CreateDuplicateElementError(string elementName, int line, int column)
        {
            return new DotlException($"Element '{elementName}' is already defined", line, column, "DUPLICATE_ELEMENT");
        }

        public static DotlException CreateUndefinedElementError(string elementName, int line, int column)
        {
            return new DotlException($"Element '{elementName}' is not defined", line, column, "UNDEFINED_ELEMENT");
        }

        public static DotlException CreateCircularReferenceError(string containerName, string childName, int line, int column)
        {
            return new DotlException($"Circular reference detected: {containerName} cannot contain {childName} which already contains {containerName}", line, column, "CIRCULAR_REFERENCE");
        }

        public static string FormatError(DotlException ex, string[]? sourceLines = null)
        {
            var builder = new StringBuilder();
            builder.AppendLine($"Error: {ex.Message}");
            builder.AppendLine($"Code: {ex.ErrorCode}");

            if (sourceLines != null && ex.Line > 0 && ex.Line <= sourceLines.Length)
            {
                builder.AppendLine($"Line {ex.Line}: {sourceLines[ex.Line - 1].Trim()}");

                // Add arrow pointing to the error position
                var spaces = new string(' ', ex.Column - 1);
                builder.AppendLine($"{spaces}^");
            }

            return builder.ToString();
        }
    }
}