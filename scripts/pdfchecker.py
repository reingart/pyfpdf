#!/usr/bin/env python3

# Invoke Datalogics PDF Checker & parse its output
# Purpose of this script:
# * abort the validation pipeline with a non-zero error code if any check fails on a PDF sample
# * aggregate all checks performed in a concise summary
# * parallelize the execution of this analysis on all PDF files
# * allow to ignore some errors considered harmless, listed in pdfchecker-ignore.json

# USAGE: ./pdfchecker.py [$pdf_filepath|--process-all-test-pdf-files|--print-aggregated-report]

import sys
from subprocess import check_output

from scripts.checker_commons import main

CHECKS_DETAILS_URL = "https://dev.datalogics.com/pdf-checker/the-json-profile-file/description-of-json-profile-parameters/"
UNPROCESSABLE_PDF_ERROR_LINE = "Unable to process document due to PDF Error"
CHECKER_SUMMARY_END_LINE = "<<=CHECKER_SUMMARY_END=>>"


def analyze_pdf_file(pdf_filepath):
    command = [
        "PDF_Checker/pdfchecker",
        "--profile",
        "PDF_Checker/CheckerProfiles/everything.json",
        "--input",
        pdf_filepath,
        "--password",
        "fpdf2",
    ]
    # print(" ".join(command))
    output = check_output(command).decode()
    # print(output)
    return pdf_filepath, parse_output(output)


def parse_output(output):
    """
    Parse PDF Checker indented output into a dict-tree.
    Tree leaves are empty dicts.
    """
    lines = output.splitlines()
    version = lines[0]
    if UNPROCESSABLE_PDF_ERROR_LINE in lines:
        return {
            "failure": UNPROCESSABLE_PDF_ERROR_LINE,
            "version": version,
        }
    assert CHECKER_SUMMARY_END_LINE in lines, "\n".join(lines)
    lines = lines[lines.index(CHECKER_SUMMARY_END_LINE) + 2 :]
    analysis = insert_indented(lines)
    return {
        "errors": [
            error
            for section in analysis.values()
            for error in section.get("Errors:", {}).keys()
            if error != "None"
        ],
        "version": version,
    }


def insert_indented(lines, node=None, depth=0, indent=0):
    if node is None:
        node = {}
    prev_node = None
    while lines:
        line = lines[0]
        if not line:
            lines.pop(0)
            continue
        line_indent = len(line) - len(line.lstrip())
        text = line[line_indent:].rstrip()
        if line_indent >= indent and text in (
            "Color Images",
            "Grayscale Images",
            "Monochrome Images",
        ):
            if depth > 1:
                # Leaving this branch of the tree after processing a "* Images" block
                return
            # Special case handled by creating a subnode for this "* Images" block:
            lines.pop(0)
            node[text] = {}
            insert_indented(lines, node[text], depth + 1, indent)
            continue
        if line_indent == indent:
            lines.pop(0)
            prev_node = node[text] = {}
            continue
        if line_indent > indent:
            if prev_node is None:
                # Case of more than 1 level of indentation, e.g. "How To Optimize:" section
                lines.pop(0)
                node[text] = {}
                continue
            assert (
                prev_node is not None
            ), f"depth={depth} indent={indent} line_indent={line_indent}: {line}"
            insert_indented(lines, prev_node, depth + 1, indent + 4)
            continue
        return  # line_indent < indent
    return node


if __name__ == "__main__":
    main("pdfchecker", analyze_pdf_file, sys.argv, CHECKS_DETAILS_URL)
