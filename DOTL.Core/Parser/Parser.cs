using DOTL.Core.Parser.AST;

namespace DOTL.Core.Parser
{
    public class Parser
    {
        private readonly List<Token> _tokens;
        private int _current;

        public Parser(IEnumerable<Token> tokens)
        {
            _tokens = tokens.Where(t => t.Type != TokenType.Whitespace && t.Type != TokenType.Comment).ToList();
            _current = 0;
        }

        public List<ASTNode> Parse()
        {
            var nodes = new List<ASTNode>();

            while (!IsAtEnd())
            {
                try
                {
                    var node = ParseStatement();
                    if (node != null)
                    {
                        nodes.Add(node);
                    }
                }
                catch (Exception ex)
                {
                    throw new Exception($"Parse error at line {Peek().Line}, column {Peek().Column}: {ex.Message}");
                }
            }

            return nodes;
        }

        private ASTNode ParseStatement()
        {
            if (Match(TokenType.ElementType))
            {
                return ParseElementCreation();
            }
            else if (Match(TokenType.VariableName))
            {
                return ParsePropertyAssignment();
            }
            else
            {
                throw new Exception($"Unexpected token '{Peek().Value}'. Expected element type or variable name.");
            }
        }

        private ASTNode ParseElementCreation()
        {
            var elementTypeToken = Previous();
            var elementType = elementTypeToken.Value;

            // Expect .create
            Consume(TokenType.Create, $"Expected '.create' after element type '{elementType}'");

            // Expect =
            Consume(TokenType.Equals, "Expected '=' after '.create'");

            // Expect variable name
            var variableNameToken = Consume(TokenType.VariableName, "Expected variable name after '='");

            return new ElementCreationNode(elementType, variableNameToken.Value, elementTypeToken.Line, elementTypeToken.Column);
        }

        private ASTNode ParsePropertyAssignment()
        {
            var variableNameToken = Previous();
            var variableName = variableNameToken.Value;

            // Check if this is a container add operation or property assignment
            if (Match(TokenType.Add))
            {
                // Container add: container.add = child
                Consume(TokenType.Equals, "Expected '=' after '.add'");
                var childVariableToken = Consume(TokenType.VariableName, "Expected child variable name after '='");
                return new ContainerAddNode(variableName, childVariableToken.Value, variableNameToken.Line, variableNameToken.Column);
            }
            else if (Match(TokenType.Dot))
            {
                // Property assignment: variable.property = "value"
                var propertyToken = Previous();
                var propertyName = propertyToken.Value.TrimStart('.');

                Consume(TokenType.Equals, $"Expected '=' after property name '{propertyName}'");
                var valueToken = Consume(TokenType.StringValue, $"Expected string value after '=' for property '{propertyName}'");

                return new PropertyAssignmentNode(variableName, propertyName, valueToken.Value, variableNameToken.Line, variableNameToken.Column);
            }
            else
            {
                throw new Exception($"Expected '.add' or '.<property>' after variable name '{variableName}'");
            }
        }

        private Token Consume(TokenType type, string message)
        {
            if (Check(type))
            {
                return Advance();
            }

            throw new Exception($"{message}. Got '{Peek().Value}' instead.");
        }

        private bool Match(TokenType type)
        {
            if (Check(type))
            {
                Advance();
                return true;
            }
            return false;
        }

        private bool Check(TokenType type)
        {
            if (IsAtEnd()) return false;
            return Peek().Type == type;
        }

        private Token Advance()
        {
            if (!IsAtEnd()) _current++;
            return Previous();
        }

        private bool IsAtEnd()
        {
            return _current >= _tokens.Count;
        }

        private Token Peek()
        {
            if (IsAtEnd()) return _tokens[_tokens.Count - 1];
            return _tokens[_current];
        }

        private Token Previous()
        {
            return _tokens[_current - 1];
        }
    }
}