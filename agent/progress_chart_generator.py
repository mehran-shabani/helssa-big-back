#!/usr/bin/env python3
"""
SVG Progress Chart Generator for HELSSA Agent Apps
Generates doughnut charts showing progress for each application
"""

import json
import math
from pathlib import Path

def generate_doughnut_svg(completed_percentage, app_name, total_items, completed_items):
    """
    Generate an SVG doughnut chart for progress visualization
    """
    # Chart dimensions
    width = 300
    height = 300
    center_x = width // 2
    center_y = height // 2
    outer_radius = 100
    inner_radius = 60
    
    # Calculate angle for completed portion (in radians)
    # Start from top (-90 degrees)
    start_angle = -math.pi / 2
    end_angle = start_angle + (completed_percentage / 100) * 2 * math.pi
    
    # Calculate path for completed arc
    def polar_to_cartesian(angle, radius):
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        return x, y
    
    # Points for the arc
    start_outer = polar_to_cartesian(start_angle, outer_radius)
    end_outer = polar_to_cartesian(end_angle, outer_radius)
    start_inner = polar_to_cartesian(start_angle, inner_radius)
    end_inner = polar_to_cartesian(end_angle, inner_radius)
    
    # Determine if arc is large (> 180 degrees)
    large_arc = 1 if completed_percentage > 50 else 0
    
    # Create SVG path for completed portion
    if completed_percentage == 0:
        completed_path = ""
    elif completed_percentage == 100:
        # Full circle - draw two semicircles
        mid_outer = polar_to_cartesian(start_angle + math.pi, outer_radius)
        mid_inner = polar_to_cartesian(start_angle + math.pi, inner_radius)
        
        completed_path = f"""
        M {start_outer[0]} {start_outer[1]}
        A {outer_radius} {outer_radius} 0 0 1 {mid_outer[0]} {mid_outer[1]}
        A {outer_radius} {outer_radius} 0 0 1 {start_outer[0]} {start_outer[1]}
        L {start_inner[0]} {start_inner[1]}
        A {inner_radius} {inner_radius} 0 0 0 {mid_inner[0]} {mid_inner[1]}
        A {inner_radius} {inner_radius} 0 0 0 {start_inner[0]} {start_inner[1]}
        Z
        """
    else:
        completed_path = f"""
        M {start_outer[0]} {start_outer[1]}
        A {outer_radius} {outer_radius} 0 {large_arc} 1 {end_outer[0]} {end_outer[1]}
        L {end_inner[0]} {end_inner[1]}
        A {inner_radius} {inner_radius} 0 {large_arc} 0 {start_inner[0]} {start_inner[1]}
        Z
        """
    
    # Choose colors based on progress
    if completed_percentage < 25:
        color = "#ef4444"  # Red
    elif completed_percentage < 50:
        color = "#f97316"  # Orange
    elif completed_percentage < 75:
        color = "#eab308"  # Yellow
    elif completed_percentage < 100:
        color = "#22c55e"  # Green
    else:
        color = "#059669"  # Dark Green
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Background circle -->
    <circle cx="{center_x}" cy="{center_y}" r="{outer_radius}" fill="#f3f4f6" stroke="#e5e7eb" stroke-width="2"/>
    <circle cx="{center_x}" cy="{center_y}" r="{inner_radius}" fill="white"/>
    
    <!-- Completed portion -->
    <path d="{completed_path}" fill="{color}" opacity="0.9"/>
    
    <!-- Center text -->
    <text x="{center_x}" y="{center_y - 15}" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#374151">
        {completed_percentage}%
    </text>
    
    <!-- App name -->
    <text x="{center_x}" y="{center_y + 5}" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#6b7280">
        {app_name}
    </text>
    
    <!-- Progress details -->
    <text x="{center_x}" y="{center_y + 25}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#9ca3af">
        {completed_items}/{total_items} مکمل
    </text>
    
    <!-- Legend -->
    <rect x="20" y="20" width="15" height="15" fill="{color}" opacity="0.9"/>
    <text x="40" y="32" font-family="Arial, sans-serif" font-size="12" fill="#374151">تکمیل شده</text>
    
    <rect x="20" y="40" width="15" height="15" fill="#f3f4f6" stroke="#e5e7eb" stroke-width="1"/>
    <text x="40" y="52" font-family="Arial, sans-serif" font-size="12" fill="#374151">باقی‌مانده</text>
</svg>'''
    
    return svg_content

def create_progress_chart_for_app(app_path):
    """
    Create progress chart for a specific app based on its CHECKLIST.json
    """
    checklist_path = Path(app_path) / "CHECKLIST.json"
    
    if not checklist_path.exists():
        print(f"Warning: No CHECKLIST.json found for {app_path}")
        return
    
    try:
        with open(checklist_path, 'r', encoding='utf-8') as f:
            checklist = json.load(f)
        
        app_name = checklist.get('app', 'Unknown')
        total_items = len(checklist.get('items', []))
        completed_items = sum(1 for item in checklist.get('items', []) if item.get('done', False))
        
        completed_percentage = round((completed_items / total_items) * 100) if total_items > 0 else 0
        
        # Generate SVG
        svg_content = generate_doughnut_svg(completed_percentage, app_name, total_items, completed_items)
        
        # Create charts directory if it doesn't exist
        charts_dir = Path(app_path) / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        # Save SVG file
        svg_path = charts_dir / "progress_doughnut.svg"
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"✅ Progress chart created for {app_name}: {completed_percentage}% ({completed_items}/{total_items})")
        
        return {
            'app': app_name,
            'percentage': completed_percentage,
            'completed': completed_items,
            'total': total_items,
            'svg_path': str(svg_path)
        }
        
    except Exception as e:
        print(f"Error creating progress chart for {app_path}: {e}")
        return None

def main():
    """
    Generate progress charts for all apps in the agent directory
    """
    agent_dir = Path(__file__).parent
    apps_dir = agent_dir / "apps"
    
    print("🎯 Generating Progress Charts for HELSSA Apps")
    print("=" * 50)
    
    results = []
    
    # Find all app directories under agent/apps
    search_root = apps_dir if apps_dir.exists() else agent_dir
    for app_dir in search_root.iterdir():
        if not app_dir.is_dir():
            continue
        if app_dir.name.startswith('.'):
            continue
        if app_dir.name in ['TEMPLATES', '__pycache__', 'docs']:
            continue

        result = create_progress_chart_for_app(app_dir)
        if result:
            results.append(result)
    
    print("\n📊 Summary:")
    print("-" * 30)
    
    total_apps = len(results)
    total_items = sum(r['total'] for r in results)
    total_completed = sum(r['completed'] for r in results)
    overall_percentage = round((total_completed / total_items) * 100) if total_items > 0 else 0
    
    for result in results:
        status_emoji = "🟢" if result['percentage'] == 100 else "🟡" if result['percentage'] >= 50 else "🔴"
        print(f"{status_emoji} {result['app']}: {result['percentage']}% ({result['completed']}/{result['total']})")
    
    print(f"\n🎯 Overall Progress: {overall_percentage}% ({total_completed}/{total_items} tasks across {total_apps} apps)")

if __name__ == "__main__":
    main()