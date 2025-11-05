using System.Collections.Generic;
using DOTL.Core.Elements;

namespace DOTL.Core.Runtime
{
    public class ElementRegistry
    {
        private readonly Dictionary<string, HtmlElement> _elements;

        public ElementRegistry()
        {
            _elements = new Dictionary<string, HtmlElement>();
        }

        public void RegisterElement(string name, HtmlElement element)
        {
            if (_elements.ContainsKey(name))
            {
                throw new InvalidOperationException($"Element with name '{name}' is already registered.");
            }

            _elements[name] = element;
        }

        public HtmlElement GetElement(string name)
        {
            if (_elements.TryGetValue(name, out var element))
            {
                return element;
            }

            throw new KeyNotFoundException($"Element with name '{name}' not found. Available elements: {string.Join(", ", _elements.Keys)}");
        }

        public bool HasElement(string name)
        {
            return _elements.ContainsKey(name);
        }

        public void AddChild(string parentName, string childName)
        {
            var parent = GetElement(parentName);
            var child = GetElement(childName);

            parent.Children.Add(child);
        }

        public void SetProperty(string elementName, string propertyName, string value)
        {
            var element = GetElement(elementName);
            element.SetProperty(propertyName, value);
        }

        public IEnumerable<HtmlElement> GetAllElements()
        {
            return _elements.Values;
        }

        public IEnumerable<HtmlElement> GetRootElements()
        {
            // Return elements that are not children of any other element
            var allChildElements = new HashSet<string>();

            foreach (var element in _elements.Values)
            {
                foreach (var child in element.Children)
                {
                    allChildElements.Add(child.Name);
                }
            }

            return _elements.Values.Where(e => !allChildElements.Contains(e.Name));
        }

        public void Clear()
        {
            _elements.Clear();
        }

        public int Count => _elements.Count;

        public override string ToString()
        {
            return $"ElementRegistry with {_elements.Count} elements";
        }
    }
}