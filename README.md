# CVFL

Used for maintaining the governing documents of the Capitol Valley Forensics League

The files here are *not* the source of truth for these documents. These files are intermediaries, used to help show the differences between revisions.

For official documentation details, see the CVFL website at cvfl.org/constitution.

## Stuff for Nerds

In order to convert these Markdown documents to a PDF that uses 1/A/i/a numbering format, you can use Pandoc.

### Pandoc Steps

1. Install `pandoc` using these instructions: https://pandoc.org/installing.html. Easiest approach is to install the binary into the same folder where your Markdown files live, unless you are planning on reusing this tool in many locations.
2. Install a LaTex editor such as [MikTeX](https://miktex.org/download). You may also need to add the folder containing the installed `pdflatex` binary to your environment's `$env:PATH` variable (ex. `$env:PATH+=";${env:LOCALAPPDATA}\Programs\MiKTeX\miktex\bin\x64"`)
3. In a terminal, such as Windows PowerShell, run `./pandoc cvfl_bylaws.md -o cvfl_bylaws.pdf`.
    1. Approve the installations of supporting LaTeX `.sty` files when prompted.
    2. You can change the source file and output file depending on which document you would like to generate.
