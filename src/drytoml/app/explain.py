from drytoml.parser import Parser

def explain(file="pyproject.toml"):
    """Show steps for toml injection"""
    parser = Parser.from_file(file)
    document = parser.parse()
