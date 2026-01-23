#!/usr/bin/env python3

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

def get_svg_content(svg_path):
    """Read and parse an SVG file, returning its root element and dimensions."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Get width and height
    width = root.get('width', '100%')
    height = root.get('height', '100%')
    
    # Get viewBox
    viewBox = root.get('viewBox')
    if viewBox:
        # Parse viewBox into min-x, min-y, width, height
        min_x, min_y, vb_width, vb_height = map(float, viewBox.split())
    else:
        # If no viewBox, try to get width and height as numbers
        try:
            vb_width = float(width.rstrip('px'))
            vb_height = float(height.rstrip('px'))
            min_x, min_y = 0, 0
        except ValueError:
            # Default to 1000x1000 if we can't determine size
            min_x, min_y = 0, 0
            vb_width, vb_height = 1000, 1000
    
    return root, width, height, f"{min_x} {min_y} {vb_width} {vb_height}"

def create_combined_svg(svg1_path, svg2_path, output_path):
    """Create a new SVG that overlays two SVGs with color filters."""
    
    # Get content and dimensions from first SVG
    svg1_root, width, height, viewBox = get_svg_content(svg1_path)
    _, _, _, _ = get_svg_content(svg2_path)  # Just to verify second SVG exists
    
    # Create the root SVG element
    root = ET.Element('svg')
    root.set('xmlns', 'http://www.w3.org/2000/svg')
    root.set('version', '1.1')
    root.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
    root.set('width', width)
    root.set('height', height)
    root.set('viewBox', viewBox)
    
    # Add the defs section with filters
    defs = ET.SubElement(root, 'defs')
    
    # Filter for first commit (cyan #00FFFF)
    filter1 = ET.SubElement(defs, 'filter')
    filter1.set('id', 'filter-1')
    feColorMatrix1 = ET.SubElement(filter1, 'feColorMatrix')
    feColorMatrix1.set('in', 'SourceGraphic')
    feColorMatrix1.set('type', 'matrix')
    feColorMatrix1.set('values', '1.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 1.0 0.0 0.0 0.0 1.0 1.0 0.0 0.0 0.0 0.0 1.0 0.0')
    
    # Filter for second commit (red #880808)
    filter2 = ET.SubElement(defs, 'filter')
    filter2.set('id', 'filter-2')
    feColorMatrix2 = ET.SubElement(filter2, 'feColorMatrix')
    feColorMatrix2.set('in', 'SourceGraphic')
    feColorMatrix2.set('type', 'matrix')
    feColorMatrix2.set('values', '1.0 0.0 0.0 1.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.5 0.0')
    
    # Create a group for the viewport
    viewport = ET.SubElement(root, 'g')
    viewport.set('class', 'my_svg-pan-zoom_viewport')
    
    # Add a dark gray background
    background = ET.SubElement(viewport, 'rect')
    background.set('width', width)
    background.set('height', height)
    background.set('fill', '#222222')
    
    # Create groups for each SVG with their filters
    group1 = ET.SubElement(viewport, 'g')
    group1.set('filter', 'url(#filter-1)')
    
    group2 = ET.SubElement(viewport, 'g')
    group2.set('filter', 'url(#filter-2)')
    
    # Copy content from first SVG
    for child in svg1_root:
        if child.tag != '{http://www.w3.org/2000/svg}defs':  # Skip defs to avoid conflicts
            group1.append(ET.fromstring(ET.tostring(child)))
    
    # Copy content from second SVG
    svg2_root, _, _, _ = get_svg_content(svg2_path)
    for child in svg2_root:
        if child.tag != '{http://www.w3.org/2000/svg}defs':  # Skip defs to avoid conflicts
            group2.append(ET.fromstring(ET.tostring(child)))
    
    # Write the combined SVG
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

def main():
    parser = argparse.ArgumentParser(description='Combine and colorize schematic SVGs from two commits')
    parser.add_argument('commit1', help='First commit hash')
    parser.add_argument('commit2', help='Second commit hash')
    parser.add_argument('--output-dir', default='combined_schematics', help='Output directory for combined SVGs')
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Get paths to SVG directories
    svg_dir1 = Path(f'.kiri/{args.commit1}/_KIRI_/sch')
    svg_dir2 = Path(f'.kiri/{args.commit2}/_KIRI_/sch')
    
    if not svg_dir1.exists() or not svg_dir2.exists():
        print(f"Error: SVG directories not found for commits {args.commit1} and/or {args.commit2}")
        print(f"Expected directories:")
        print(f"  {svg_dir1}")
        print(f"  {svg_dir2}")
        sys.exit(1)
    
    # Get list of SVG files
    svg_files1 = list(svg_dir1.glob('*.svg'))
    svg_files2 = list(svg_dir2.glob('*.svg'))
    
    if not svg_files1 or not svg_files2:
        print("Error: No SVG files found in one or both directories")
        sys.exit(1)
    
    # Create a set of all SVG filenames
    all_svg_names = {f.name for f in svg_files1 + svg_files2}
    
    # Process each SVG file
    for svg_name in all_svg_names:
        svg1_path = svg_dir1 / svg_name
        svg2_path = svg_dir2 / svg_name
        
        # Skip if either file is missing
        if not svg1_path.exists() or not svg2_path.exists():
            print(f"Skipping {svg_name} - missing in one or both commits")
            continue
        
        # Create combined SVG
        output_path = output_dir / f'combined_{svg_name}'
        print(f"Creating {output_path}")
        create_combined_svg(svg1_path, svg2_path, output_path)
    
    print(f"\nCombined SVGs have been created in {output_dir}/")
    print("The first commit is shown in cyan (#00FFFF), the second in red (#880808).")
    print("Unchanged elements will appear white (#FFFFFF) on a dark gray (#222222) background.")

if __name__ == '__main__':
    main() 