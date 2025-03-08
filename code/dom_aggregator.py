"""
Aggregates the DOM trees of multiples JSONs into an aggregated JSON.
"""

import json
import os
import statistics
from collections import defaultdict


class DomAggregator:
    """Aggregates the DOM trees of multiples JSONs into an aggregated JSON."""

    def __init__(self, doms_dir):
        self.doms_dir = doms_dir
        self.doms = []
        self.aggregated_dom = {}

    def load_doms(self):
        """Load all DOM JSON files from the directory"""
        for file in os.listdir(self.doms_dir):
            if file.endswith('.json'):
                file_path = os.path.join(self.doms_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    dom = json.load(f)
                    self.doms.append(dom)
        return len(self.doms)

    def aggregate(self):
        """Aggregate all DOM trees with frequency information"""
        if not self.doms:
            self.load_doms()

        self.aggregated_dom = self._aggregate_structure(self.doms)
        return self.aggregated_dom

    def _aggregate_structure(self, doms):
        """
        Aggregate DOM structures while preserving the original structure
        and providing statistical measures
        """
        # First, identify all unique paths in the DOM structure
        path_occurrences = self._analyze_paths(doms)

        # Create the aggregated structure
        return self._build_aggregated_structure(path_occurrences)

    def _analyze_paths(self, doms, current_path=None):
        """
        Analyze all paths in the DOM structures and count their occurrences
        Returns a dictionary mapping paths to their occurrence counts
        """
        if current_path is None:
            current_path = []

        # Dictionary to store path occurrences
        path_occurrences = defaultdict(list)

        # For each DOM, traverse and record paths
        for dom_idx, dom in enumerate(doms):
            self._traverse_dom(dom, dom_idx, current_path, path_occurrences)

        return path_occurrences

    def _traverse_dom(self, dom, dom_idx, current_path, path_occurrences):
        """
        Traverse a DOM structure and record all paths
        """
        if not isinstance(dom, dict):
            return

        for tag, children in dom.items():
            # Create a new path by appending the current tag
            new_path = current_path + [tag]
            path_key = tuple(new_path)

            # Record that this path exists in this DOM
            path_occurrences[path_key].append(dom_idx)

            # Recursively traverse children
            if children:
                for child in children:
                    self._traverse_dom(
                        child, dom_idx, new_path, path_occurrences)

    def _build_aggregated_structure(self, path_occurrences):
        """
        Build the aggregated structure from path occurrences
        """
        # Sort paths by length to ensure we build from root to leaves
        sorted_paths = sorted(path_occurrences.keys(), key=len)

        # The aggregated structure
        aggregated = {}

        # Build the structure
        for path in sorted_paths:
            occurrences = path_occurrences[path]

            # Calculate statistics
            stats = {
                # Number of unique DOMs containing this path
                "count": len(set(occurrences)),
                # Total occurrences across all DOMs
                "total_occurrences": len(occurrences),
                # % of DOMs containing this path
                "percentage": round(len(set(occurrences)) / len(self.doms) * 100, 2)
            }

            # Add min, max, mean, median if the tag appears inconsistently
            if stats["count"] < len(self.doms):
                # Count occurrences per DOM
                dom_counts = defaultdict(int)
                for dom_idx in occurrences:
                    dom_counts[dom_idx] += 1

                # Only include non-zero counts (DOMs where the tag appears)
                non_zero_counts = [
                    count for count in dom_counts.values() if count > 0]

                if non_zero_counts:
                    stats["min"] = min(non_zero_counts)
                    stats["max"] = max(non_zero_counts)
                    stats["mean"] = round(statistics.mean(non_zero_counts), 2)
                    stats["median"] = round(
                        statistics.median(non_zero_counts), 2)

            # Insert this path with its stats into the aggregated structure
            self._insert_path(aggregated, path, stats)

        return aggregated

    def _insert_path(self, structure, path, stats):
        """
        Insert a path with its statistics into the aggregated structure
        """
        if not path:
            return

        current = structure
        for i, tag in enumerate(path):
            # If this is the last tag in the path, add it with stats
            if i == len(path) - 1:
                if tag not in current:
                    current[tag] = {"stats": stats, "children": {}}
                else:
                    # Update stats if the tag already exists
                    current[tag]["stats"] = stats
            else:
                # Create intermediate nodes if they don't exist
                if tag not in current:
                    current[tag] = {"stats": {"count": 0}, "children": {}}

                current = current[tag]["children"]

    def to_json(self):
        """Return the aggregated DOM as a JSON string"""
        if not self.aggregated_dom:
            self.aggregate()
        return json.dumps(self.aggregated_dom, indent=2)

    def save_to_file(self, output_path):
        """Save the aggregated DOM to a JSON file"""
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(self.to_json())
