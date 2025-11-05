using System.CommandLine;
using DOTL.Core.Parser;
using DOTL.Core.Generator;

namespace DOTL.CLI
{
    class Program
    {
        static async Task<int> Main(string[] args)
        {
            var rootCommand = new RootCommand("DOTL - Domain-Oriented Text Language Compiler");

            var inputOption = new Option<string>(
                name: "--input",
                description: "Path to the .dotl file to compile")
            {
                IsRequired = true
            };

            var outputOption = new Option<string>(
                name: "--output",
                description: "Path to the output .html file")
            {
                IsRequired = false
            };

            var validateOption = new Option<bool>(
                name: "--validate",
                description: "Only validate the syntax without generating HTML")
            {
                IsRequired = false
            };

            rootCommand.AddOption(inputOption);
            rootCommand.AddOption(outputOption);
            rootCommand.AddOption(validateOption);

            rootCommand.SetHandler(async (input, output, validate) =>
            {
                try
                {
                    await CompileDotlFile(input, output, validate);
                }
                catch (Exception ex)
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine($"Error: {ex.Message}");
                    Console.ResetColor();
                    Environment.ExitCode = 1;
                }
            }, inputOption, outputOption, validateOption);

            return await rootCommand.InvokeAsync(args);
        }

        static async Task CompileDotlFile(string inputPath, string? outputPath, bool validateOnly)
        {
            if (!File.Exists(inputPath))
            {
                throw new FileNotFoundException($"Input file not found: {inputPath}");
            }

            Console.WriteLine($"Reading DOTL file: {inputPath}");

            var dotlContent = await File.ReadAllTextAsync(inputPath);

            // Create lexer and tokenize
            Console.WriteLine("Tokenizing...");
            var lexer = new Lexer(dotlContent);
            var tokens = lexer.Tokenize().ToList();

            Console.WriteLine($"Found {tokens.Count} tokens");

            // Create parser and parse AST
            Console.WriteLine("Parsing...");
            var parser = new Parser(tokens);
            var astNodes = parser.Parse();

            Console.WriteLine($"Parsed {astNodes.Count} statements");

            if (validateOnly)
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("✓ Syntax validation passed!");
                Console.ResetColor();
                return;
            }

            // Generate HTML
            Console.WriteLine("Generating HTML...");
            var generator = new HtmlGenerator();
            var htmlOutput = generator.Generate(astNodes);

            // Determine output path
            var finalOutputPath = outputPath ?? Path.ChangeExtension(inputPath, ".html");

            // Write output
            await File.WriteAllTextAsync(finalOutputPath, htmlOutput);

            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine($"✓ Successfully generated HTML: {finalOutputPath}");
            Console.ResetColor();
        }
    }
}