using System.Text.RegularExpressions;

namespace DOTL.Core.Parser
{
    public enum TokenType
    {
        ElementType,      // txt, h1, p, div, etc.
        Create,           // .create
        VariableName,     // exampleName, header, etc.
        Equals,           // =
        StringValue,      // "text in quotes"
        Dot,              // .
        PropertyName,     // Text, Class, Style, etc.
        Add,              // .add
        Comment,          // # comment line
        Whitespace,       // spaces, tabs, newlines
        Unknown
    }

    public class Token
    {
        public TokenType Type { get; }
        public string Value { get; }
        public int Line { get; }
        public int Column { get; }

        public Token(TokenType type, string value, int line, int column)
        {
            Type = type;
            Value = value;
            Line = line;
            Column = column;
        }

        public override string ToString()
        {
            return $"{Type}: '{Value}' at {Line}:{Column}";
        }
    }

    public class Lexer
    {
        private static readonly Dictionary<string, TokenType> Keywords = new()
        {
            { ".create", TokenType.Create },
            { ".add", TokenType.Add }
        };

        private static readonly string[] ElementTypes = {
            "txt", "h1", "h2", "h3", "p", "div", "section", "header", "footer", "nav",
            "main", "article", "aside", "form", "input", "btn", "select", "textarea",
            "img", "video", "audio", "link", "table", "list", "ul", "ol", "li", "span"
        };

        private readonly string _input;
        private int _position;
        private int _line;
        private int _column;

        public Lexer(string input)
        {
            _input = input ?? throw new ArgumentNullException(nameof(input));
            _position = 0;
            _line = 1;
            _column = 1;
        }

        public IEnumerable<Token> Tokenize()
        {
            var tokens = new List<Token>();

            while (_position < _input.Length)
            {
                var currentChar = _input[_position];

                if (char.IsWhiteSpace(currentChar))
                {
                    tokens.Add(ReadWhitespace());
                }
                else if (currentChar == '#')
                {
                    tokens.Add(ReadComment());
                }
                else if (currentChar == '"')
                {
                    tokens.Add(ReadString());
                }
                else if (currentChar == '=')
                {
                    tokens.Add(new Token(TokenType.Equals, "=", _line, _column));
                    _position++;
                    _column++;
                }
                else if (currentChar == '.')
                {
                    var dotToken = ReadDotExpression();
                    if (dotToken != null)
                        tokens.Add(dotToken);
                }
                else if (char.IsLetter(currentChar))
                {
                    tokens.Add(ReadIdentifier());
                }
                else
                {
                    tokens.Add(new Token(TokenType.Unknown, currentChar.ToString(), _line, _column));
                    _position++;
                    _column++;
                }
            }

            return tokens;
        }

        private Token ReadWhitespace()
        {
            var startColumn = _column;
            var value = "";

            while (_position < _input.Length && char.IsWhiteSpace(_input[_position]))
            {
                if (_input[_position] == '\n')
                {
                    value += _input[_position];
                    _position++;
                    _line++;
                    _column = 1;
                }
                else
                {
                    value += _input[_position];
                    _position++;
                    _column++;
                }
            }

            return new Token(TokenType.Whitespace, value, _line, startColumn);
        }

        private Token ReadComment()
        {
            var startColumn = _column;
            var value = "";

            // Skip the #
            _position++;
            _column++;

            // Read until end of line
            while (_position < _input.Length && _input[_position] != '\n')
            {
                value += _input[_position];
                _position++;
                _column++;
            }

            return new Token(TokenType.Comment, "#" + value, _line, startColumn);
        }

        private Token ReadString()
        {
            var startColumn = _column;
            var value = "";

            // Skip opening quote
            _position++;
            _column++;

            while (_position < _input.Length && _input[_position] != '"')
            {
                if (_input[_position] == '\n')
                {
                    throw new Exception($"Unterminated string at line {_line}, column {startColumn}");
                }

                value += _input[_position];
                _position++;
                _column++;
            }

            if (_position >= _input.Length)
            {
                throw new Exception($"Unterminated string at line {_line}, column {startColumn}");
            }

            // Skip closing quote
            _position++;
            _column++;

            return new Token(TokenType.StringValue, value, _line, startColumn);
        }

        private Token? ReadDotExpression()
        {
            var startColumn = _column;
            var value = ".";

            // Skip the dot
            _position++;
            _column++;

            // Read the identifier after the dot
            while (_position < _input.Length && (char.IsLetterOrDigit(_input[_position]) || _input[_position] == '_'))
            {
                value += _input[_position];
                _position++;
                _column++;
            }

            // Check if it's a known keyword
            if (Keywords.TryGetValue(value, out var tokenType))
            {
                return new Token(tokenType, value, _line, startColumn);
            }

            // If not a keyword, treat as a property access
            return new Token(TokenType.Dot, value, _line, startColumn);
        }

        private Token ReadIdentifier()
        {
            var startColumn = _column;
            var value = "";

            while (_position < _input.Length && (char.IsLetterOrDigit(_input[_position]) || _input[_position] == '_'))
            {
                value += _input[_position];
                _position++;
                _column++;
            }

            // Check if it's an element type
            if (ElementTypes.Contains(value.ToLower()))
            {
                return new Token(TokenType.ElementType, value.ToLower(), _line, startColumn);
            }

            // Otherwise it's a variable name
            return new Token(TokenType.VariableName, value, _line, startColumn);
        }
    }
}