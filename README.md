# ConvertMd

ConvertMd is a Sublime Text plugin that allows to directly converts markdown file to PDF file using Pandoc and LaTeX. It simplify the edition of markdown file in sublime text, by enabling a fast viewer for markdown.

Moreover, ConvertMd makes possible to modify the syntax of markdown syntax, from a usual markdown syntax to a syntax that is more compatible with github viewer and reversely. Indeed, equation could not be properly rendered in some case in github and it needs a specific syntax (see [the following post on stackoverflow](https://gist.github.com/jesshart/8dd0fd56feb6afda264a0f7c3683abbf)). This project has been made for github project that has a documentation which needs to be read by doxygen (which use what I call "usual" syntax) and by github.

## Usage

Use `ctrl+shift+P` to open command palette.

1. **Convert Markdown Syntax for Current File:**
   - Write `Convert Markdown: to github syntax` to modify the syntax of the current file to be readable by github.
   - Write `Convert Markdown: to usual syntax` to modify the syntax of the current file to the "usual" markdown syntax.

2. **Convert Markdown Syntax for Full Project:**
   - Write `Convert Markdown: to github syntax (Apply to project)` to modify the syntax of all the markdown files of the current sublime project to be readable by github.
   - Write `Convert Markdown: to usual syntax (Apply to project)` to modify the syntax of all the markdown files of the current sublime project to the "usual" markdown syntax.

Moreover, in case, you don't want to convert the markdown files of a specific folder of your sublime project. For example, if you don't want to convert the syntax of the markdown located in the dependencies folder. Then you can add the following settings to you sublime-project file:

```
"settings": {
        "convert_md_syntax": {
            "ignored_folders": [
                "[Folder_Path_To_Ignored]",
            ]
        }
    }
```   

Note, that the folder path must be given relative to the root of the sublime-project. 

3. **Generate PDF:**
   - After conversion, use the plugin to generate a PDF from your Markdown file. The plugin automatically handles the conversion to LaTeX and PDF using Pandoc.


## Installation

1. **Dependencies:**
   - The plugin requires [Pandoc](https://pandoc.org/) and a LaTeX distribution installed on your system (e.g., TeX Live, MiKTeX).
   - Ensure that both Pandoc and LaTeX are accessible from your system's PATH.

2. **Installing the Plugin:**
   - Clone or download this repository into your Sublime Text `Packages` directory:
     
```bash
git clone https://github.com/yourusername/ConvertMd.git
``` 