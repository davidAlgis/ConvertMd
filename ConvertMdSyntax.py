import sublime
import sublime_plugin
import re
import os


class ConvertMdSyntax(sublime_plugin.TextCommand):
    def run(self, edit, github2usual=True, applyToProject=False):
        if applyToProject:
            # Apply conversion to all markdown files in the current project
            files_processed = self.apply_to_project(github2usual)
            sublime.message_dialog(
                "Conversion complete. {} file(s) processed.".format(files_processed))
        else:
            # Apply conversion only to the current view
            self.apply_to_view(edit, github2usual)

    def apply_to_view(self, edit, github2usual):
        # Get the content of the current view
        content = self.view.substr(sublime.Region(0, self.view.size()))

        # Replace the blocks based on the option
        if github2usual:
            content = self.replace_math_blocks(content)
            content = self.replace_inline_math(content)
            content = self.remove_dollar_around_begin(content)
        else:
            content = self.add_dollar_around_begin(content)
            content = self.replace_usual_math_blocks(content)
            content = self.replace_usual_inline_math(content)

        # Replace the content of the view with the modified content
        self.view.replace(edit, sublime.Region(0, self.view.size()), content)

    def apply_to_project(self, github2usual):
        files_processed = 0
        project_data = sublime.active_window().project_data()

        if not project_data or "folders" not in project_data:
            sublime.error_message("No project folders found.")
            return files_processed

        # Retrieve ignored folders from project settings
        settings = project_data.get(
            "settings", {}).get("convert_md_syntax", {})
        ignored_folders = settings.get("ignored_folders", [])

        # Iterate over all folders in the project
        for folder in project_data["folders"]:
            folder_path = folder.get("path")
            if not folder_path:
                continue

            # If the folder path is relative, convert it to an absolute path
            if not os.path.isabs(folder_path):
                folder_path = os.path.join(sublime.active_window().extract_variables()[
                                           'folder'], folder_path)
            folder_path = os.path.normpath(folder_path)

            # Process the directory, respecting ignored folders
            files_processed += self.process_directory(
                folder_path, github2usual, ignored_folders)

        return files_processed

    def process_directory(self, folder_path, github2usual, ignored_folders):
        files_processed = 0
        # Walk through the directory and process all Markdown files
        for root, dirs, files in os.walk(folder_path):
            # Skip ignored folders
            dirs[:] = [d for d in dirs if d not in ignored_folders]

            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    self.process_file(file_path, github2usual)
                    files_processed += 1

        return files_processed

    def process_file(self, file_path, github2usual):
        # Open the file
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Replace the blocks based on the option
        if github2usual:
            content = self.replace_math_blocks(content)
            content = self.replace_inline_math(content)
            content = self.remove_dollar_around_begin(content)
        else:
            content = self.add_dollar_around_begin(content)
            content = self.replace_usual_math_blocks(content)
            content = self.replace_usual_inline_math(content)

        # Save the modified content back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

    def replace_math_blocks(self, content):
        # Regular expression to match ```math ... ``` blocks
        math_block_pattern = re.compile(r'```math\n(.*?)\n```', re.DOTALL)

        # Replace the blocks with $$ ... $$
        content = re.sub(math_block_pattern,
                         lambda match:
                         "$$\n{}\n$$".format(match.group(1).strip()), content)

        return content

    def replace_usual_math_blocks(self, content):
        # Regular expression to match $$ ... $$ blocks, including single-line and multi-line
        usual_math_block_pattern = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)

        # Replace the blocks with ```math ... ```
        content = re.sub(usual_math_block_pattern,
                         lambda match:
                         "```math\n{}\n```".format(match.group(1).strip()), content)

        return content

    def replace_inline_math(self, content):
        # Regular expression to match $[math]$
        inline_math_pattern = re.compile(r'\$\`(.*?)\`\$')

        # Replace the inline math with $...$
        content = re.sub(inline_math_pattern,
                         lambda match:
                         "${}$".format(match.group(1).strip()), content)

        return content

    def replace_usual_inline_math(self, content):
        # Regular expression to match $[math]$
        usual_inline_math_pattern = re.compile(r'\$(.*?)\$')

        # Function to replace the inline math with $[math]$ only if it's not already in that format
        def replace_inline(match):
            math_content = match.group(1).strip()
            if not re.match(r'`.*?`', math_content):
                return "${}$".format(math_content)
            return match.group(0)

        # Replace the inline math with $[math]$
        content = re.sub(usual_inline_math_pattern, replace_inline, content)

        return content

    def remove_dollar_around_begin(self, content):
        # Regular expression to match $$ ... $$ around \begin{align}, \begin{aligned}, and \begin{equation} blocks
        begin_block_pattern = re.compile(
            r'\$\$\n(\\begin\{align\}.*?\\end\{align\}|\\begin\{aligned\}.*?\\end\{aligned\}|\\begin\{equation\}.*?\\end\{equation\})\n\$\$', re.DOTALL)

        # Remove the $$ ... $$ around \begin blocks
        content = re.sub(begin_block_pattern,
                         lambda match:
                         "\n{}\n".format(match.group(1).strip()), content)

        return content

    def add_dollar_around_begin(self, content):
        # Regular expression to match \begin{align}, \begin{aligned}, and \begin{equation} blocks without $$ ... $$
        begin_block_pattern = re.compile(
            r'\n(\\begin\{align\}.*?\\end\{align\}|\\begin\{aligned\}.*?\\end\{aligned\}|\\begin\{equation\}.*?\\end\{equation\})\n', re.DOTALL)

        # Add the $$ ... $$ around \begin blocks
        content = re.sub(begin_block_pattern,
                         lambda match:
                         "$$\n{}\n$$".format(match.group(1).strip()), content)

        return content
