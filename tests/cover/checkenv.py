# -*- coding: utf-8 -*-

# Test environment

import common

def main():
    common.log("CHECK")
    
    try:
        from fpdf import FPDF_VERSION
    except ImportError:
        FPDF_VERSION = None
    common.log("VER =", FPDF_VERSION)
    
    try:
        try:
            import Image
        except:
            from PIL import Image
    except ImportError:
        Image = None
    if Image:
        common.log("PIL = yes")
    else:
        common.log("PIL = no")



if __name__ == "__main__":
    main()
