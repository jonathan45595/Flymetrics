from html.parser import HTMLParser
import sys

class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if not self.tags:
            print(f"Error: Unexpected closing tag </{tag}> at line {self.getpos()[0]}")
            return
        last_tag, pos = self.tags.pop()
        if last_tag != tag:
            print(f"Warning: Mismatched tag </{tag}> at line {self.getpos()[0]} (expected closing for <{last_tag}> from line {pos[0]})")

def validate(filename):
    print(f"\nValidating {filename}...")
    parser = SimpleHTMLParser()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            parser.feed(f.read())
        if parser.tags:
            print("Warning: Unclosed tags remaining:")
            for tag, pos in parser.tags:
                print(f" - <{tag}> opened at line {pos[0]}")
        else:
            print("No major HTML unclosed tag issues found.")
    except Exception as e:
        print("Error reading file:", e)

validate(r"c:\Users\MIGUEL\OneDrive\Documentos\flymetrics\frontend\index.html")
validate(r"c:\Users\MIGUEL\OneDrive\Documentos\flymetrics\frontend\staff.html")
