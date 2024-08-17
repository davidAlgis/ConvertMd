import sublime
import sublime_plugin
import os
import tempfile
import subprocess
import atexit

# List to keep track of temporary files
temp_files = []


class ConvertMdToPdfCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Get the content of the current view
        content = self.view.substr(sublime.Region(0, self.view.size()))

        # Apply the ConvertMdGithub2UsualMd conversion to the content
        self.view.run_command('convert_md_syntax', {'github2usual': True})

        # Get the converted content from the view
        converted_content = self.view.substr(
            sublime.Region(0, self.view.size()))

        # Create a temporary markdown file for the converted content
        temp_converted_md_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=".md")
        temp_files.append(temp_converted_md_file.name)
        with open(temp_converted_md_file.name, 'w', encoding='utf-8') as f:
            f.write(converted_content)

        # Get the base name of the original markdown file
        original_file_name = os.path.basename(self.view.file_name())
        base_name, _ = os.path.splitext(original_file_name)

        # Define the path for the temporary PDF file
        temp_pdf_file_name = os.path.join(
            tempfile.gettempdir(), base_name + ".pdf")

        # Check if the PDF file already exists
        if not os.path.exists(temp_pdf_file_name):
            temp_files.append(temp_pdf_file_name)

        # Call pandoc to convert the converted markdown file to PDF
        try:
            process = subprocess.Popen(['pandoc', temp_converted_md_file.name, '-o', temp_pdf_file_name],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                sublime.error_message(
                    "There has been an error while generating the PDF from markdown. "
                    "We will open the translated LaTeX that generated the error:\n" + stderr.decode('utf-8'))
                # If there is an error, generate a LaTeX file instead
                self.generate_latex(temp_converted_md_file.name, base_name)
            else:
                # Open the generated PDF file in the default application
                self.open_file(temp_pdf_file_name)
        finally:
            # Reverse the conversion
            self.view.run_command('convert_md_syntax', {'github2usual': False})

    def generate_latex(self, markdown_file, base_name):
        temp_latex_file_name = os.path.join(
            tempfile.gettempdir(), base_name + ".tex")
        temp_files.append(temp_latex_file_name)

        process = subprocess.Popen(['pandoc', markdown_file, '-o', temp_latex_file_name],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            sublime.error_message(
                "Error converting to LaTeX:\n" + stderr.decode('utf-8'))
        else:
            self.open_file(temp_latex_file_name)

    def open_file(self, file_path):
        if os.name == 'nt':  # For Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # For macOS and Linux
            subprocess.call(['open', file_path])

# Register a cleanup function to remove temporary files when Sublime Text is closed


def cleanup_temp_files():
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)


atexit.register(cleanup_temp_files)
