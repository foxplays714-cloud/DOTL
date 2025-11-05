namespace DOTL.Core.Parser.AST
{
    public abstract class ASTNode
    {
        public int Line { get; }
        public int Column { get; }

        protected ASTNode(int line, int column)
        {
            Line = line;
            Column = column;
        }

        public abstract string ToString();
    }

    public class ElementCreationNode : ASTNode
    {
        public string ElementType { get; }
        public string VariableName { get; }

        public ElementCreationNode(string elementType, string variableName, int line, int column)
            : base(line, column)
        {
            ElementType = elementType;
            VariableName = variableName;
        }

        public override string ToString()
        {
            return $"ElementCreation: {ElementType}.create = {VariableName}";
        }
    }

    public class PropertyAssignmentNode : ASTNode
    {
        public string VariableName { get; }
        public string PropertyName { get; }
        public string Value { get; }

        public PropertyAssignmentNode(string variableName, string propertyName, string value, int line, int column)
            : base(line, column)
        {
            VariableName = variableName;
            PropertyName = propertyName;
            Value = value;
        }

        public override string ToString()
        {
            return $"PropertyAssignment: {VariableName}.{PropertyName} = \"{Value}\"";
        }
    }

    public class ContainerAddNode : ASTNode
    {
        public string ContainerVariableName { get; }
        public string ChildVariableName { get; }

        public ContainerAddNode(string containerVariableName, string childVariableName, int line, int column)
            : base(line, column)
        {
            ContainerVariableName = containerVariableName;
            ChildVariableName = childVariableName;
        }

        public override string ToString()
        {
            return $"ContainerAdd: {ContainerVariableName}.add = {ChildVariableName}";
        }
    }
}