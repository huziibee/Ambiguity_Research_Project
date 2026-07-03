import os
import re

def combine_markdown_files():
    # Define paths relative to the script location or project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    plan_dir = os.path.join(project_root, 'docs', 'plan')
    output_path = os.path.join(project_root, 'docs', 'full_plan.md')
    
    # 1. If full plan exists, remove it
    if os.path.exists(output_path):
        print(f"Removing existing full plan at {output_path}")
        os.remove(output_path)
        
    if not os.path.isdir(plan_dir):
        print(f"Error: Source directory {plan_dir} does not exist.")
        return
        
    # 2. Gather all .md files in docs/plan
    md_files = [f for f in os.listdir(plan_dir) if f.endswith('.md')]
    # Sort files numerically/alphabetically (e.g., 00_overview.md, 01_target_outputs.md)
    md_files.sort()
    
    if not md_files:
        print("No markdown files found to combine.")
        return
        
    combined_content = []
    
    # Regular expressions for front matter and footers
    # Front matter starts with --- and ends with ---
    front_matter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    
    print(f"Combining {len(md_files)} files from {plan_dir}...")
    
    for filename in md_files:
        file_path = os.path.join(plan_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remove front matter
        content_no_fm = front_matter_pattern.sub('', content)
        
        # Remove navigation footer
        # A footer generally starts with '---' followed by previous/next navigation text
        lines = content_no_fm.splitlines()
        clean_lines = []
        skip_footer = False
        
        # Scan from the bottom to find where the navigation footer starts
        footer_start_idx = None
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            # Look for typical footer patterns
            if line.startswith('**← Previous:**') or line.startswith('**Next →**') or line.startswith('**←**'):
                # Check if there is a '---' within 2 lines above it
                for j in range(max(0, i - 2), i):
                    if lines[j].strip() == '---':
                        footer_start_idx = j
                        break
                if footer_start_idx is not None:
                    break
        
        if footer_start_idx is not None:
            clean_lines = lines[:footer_start_idx]
        else:
            clean_lines = lines
            
        # Clean trailing empty lines
        while clean_lines and clean_lines[-1].strip() == '':
            clean_lines.pop()
            
        file_content = '\n'.join(clean_lines).strip()
        if file_content:
            combined_content.append(file_content)
            
    # Join sections with two newlines and a horizontal divider
    final_output = '\n\n---\n\n'.join(combined_content)
    
    # Write to target path
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)
        
    print(f"Successfully generated new full plan at {output_path}")

if __name__ == '__main__':
    combine_markdown_files()
