"""
Efficiently reads markup tags, and returns the DOM tree.
"""

import json

from bs4 import BeautifulSoup


class TagReader:
    """
    Reads markup tags, and returns the DOM tree.
    """
    def __init__(self, file_path):
        """
        Initialize the TagReader with the file path.
        """
        self.file_path = file_path
        self.dom = None

    def read_file(self):
        """Read the markup file content"""
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()

    def parse(self):
        """Parse the markup file and build the DOM tree"""
        content = self.read_file()

        soup = BeautifulSoup(content, 'html.parser')
        self.dom = self._build_dom_tree(soup)


    def _build_dom_tree(self, element):
        """
        Recursively build a DOM tree from a BeautifulSoup element
        Returns a dictionary with tag names as keys and lists of children as values
        """

        if element.name is None:
            for child in element.children:
                if child.name is not None:
                    return self._build_dom_tree(child)
            return {}

        result = {element.name: []}

        for child in element.children:
            if child.name is not None:
                child_tree = self._build_dom_tree(child)
                if child_tree:
                    result[element.name].append(child_tree)

        return result

    def get_dom(self):
        """Return the DOM tree"""
        if self.dom is None:
            self.parse()
        return self.dom

    def to_json(self):
        """Return the DOM tree as a JSON string"""
        if self.dom is None:
            self.parse()
        return json.dumps(self.dom, indent=2)

    def save_to_file(self, output_path):
        """Save the DOM tree to a JSON file"""
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(self.to_json())
