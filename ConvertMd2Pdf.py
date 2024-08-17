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
        result = subprocess.run(['pandoc', temp_converted_md_file.name, '-o', temp_pdf_file_name],
                                capture_output=True, text=True)

        # Check for errors
        if result.returncode != 0:
            sublime.error_message(
                "There has been an error while generating the pdf from markdown."
                "We will open the translated latex that is used to generate the pdf. Error:" + result.stderr)
            # If there is an error, generate a LaTeX file instead
            temp_latex_file_name = os.path.join(
                tempfile.gettempdir(), base_name + ".tex")
            temp_files.append(temp_latex_file_name)

            # Call pandoc to convert the converted markdown file to LaTeX
            latex_result = subprocess.run(['pandoc', temp_converted_md_file.name, '-s', '-o', temp_latex_file_name],
                                          capture_output=True, text=True)
            if latex_result.returncode != 0:
                error_message = latex_result.stderr if latex_result.stderr else latex_result.stdout
                sublime.error_message(
                    "Error converting to PDF and LaTeX:\n" + error_message)
            else:
                # Open the generated LaTeX file in the default application
                if os.name == 'nt':  # For Windows
                    os.startfile(temp_latex_file_name)
                elif os.name == 'posix':  # For macOS and Linux
                    subprocess.run(['open', temp_latex_file_name])
        else:
            # Open the generated PDF file in the default application
            if os.name == 'nt':  # For Windows
                os.startfile(temp_pdf_file_name)
            elif os.name == 'posix':  # For macOS and Linux
                subprocess.run(['open', temp_pdf_file_name])

        # Reverse the conversion
        self.view.run_command('convert_md_syntax', {'github2usual': False})

# Register a cleanup function to remove temporary files when Sublime Text is closed


def cleanup_temp_files():
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)


atexit.register(cleanup_temp_files)
