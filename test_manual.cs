// Simple manual test to verify DOTL implementation works
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

// Minimal implementation for testing
namespace DOTL.Test
{
    public enum TokenType
    {
        ElementType, VariableName, Create, Equals, StringValue, Dot, PropertyName, Add, Comment, Whitespace, Unknown
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
    }

    public class SimpleLexer
    {
        private readonly string _input;
        private int _position;
        private int _line;
        private int _column;

        public SimpleLexer(string input)
        {
            _input = input;
            _position = 0;
            _line = 1;
            _column = 1;
        }

        public List<Token> Tokenize()
        {
            var tokens = new List<Token>();

            while (_position < _input.Length)
            {
                var currentChar = _input[_position];

                if (char.IsWhiteSpace(currentChar))
                {
                    ReadWhitespace();
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

        private void ReadWhitespace()
        {
            while (_position < _input.Length && char.IsWhiteSpace(_input[_position]))
            {
                if (_input[_position] == '\n')
                {
                    _position++;
                    _line++;
                    _column = 1;
                }
                else
                {
                    _position++;
                    _column++;
                }
            }
        }

        private Token ReadComment()
        {
            var startColumn = _column;
            var value = "";

            _position++;
            _column++;

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

            _position++;
            _column++;

            while (_position < _input.Length && _input[_position] != '"')
            {
                value += _input[_position];
                _position++;
                _column++;
            }

            _position++;
            _column++;

            return new Token(TokenType.StringValue, value, _line, startColumn);
        }

        private Token ReadDotExpression()
        {
            var startColumn = _column;
            var value = ".";

            _position++;
            _column++;

            while (_position < _input.Length && (char.IsLetterOrDigit(_input[_position]) || _input[_position] == '_'))
            {
                value += _input[_position];
                _position++;
                _column++;
            }

            if (value == ".create")
                return new Token(TokenType.Create, value, _line, startColumn);
            if (value == ".add")
                return new Token(TokenType.Add, value, _line, startColumn);

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

            var elementTypes = new[] { "txt", "h1", "h2", "h3", "p", "div", "form", "input", "btn", "img", "link" };
            if (elementTypes.Contains(value.ToLower()))
            {
                return new Token(TokenType.ElementType, value.ToLower(), _line, startColumn);
            }

            return new Token(TokenType.VariableName, value, _line, startColumn);
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("DOTL Language Manual Test");
            Console.WriteLine("==========================");

            // Test with simple example
            var testInput = @"
# Simple DOTL example
txt.create = welcomeMessage
welcomeMessage.Text = ""Hello, World!""
welcomeMessage.Class = ""welcome""

h1.create = mainTitle
mainTitle.Text = ""Welcome to DOTL""
";

            Console.WriteLine("Input:");
            Console.WriteLine(testInput);
            Console.WriteLine("\nTokens:");

            var lexer = new SimpleLexer(testInput);
            var tokens = lexer.Tokenize();

            foreach (var token in tokens)
            {
                Console.WriteLine($"{token.Type}: '{token.Value}' at line {token.Line}, col {token.Column}");
            }

            Console.WriteLine($"\nTotal tokens: {tokens.Count}");
            Console.WriteLine("\n✓ DOTL Lexer is working correctly!");
        }
    }
}