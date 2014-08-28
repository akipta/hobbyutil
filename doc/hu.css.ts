.(
    import time
    date = time.strftime("%d%b%Y %H:%M%p")
    bg = "#f0f0ff"
.)

/* Constructed from hu.css.ts {date} */

body {{
    font-family: Arial, sans-serif;
    color: #000000;
    background-color: #ffffff;
    font-size:  medium;
}}

h1 {{
    font-size:  x-large;
}}

h2, h3, h4, h5, h6 {{
    font-size:  large;
}}

h1.title {{
    text-align: center;
}}

a {{
    color: #000080;
    text-decoration: underline;
    font-style: normal;
}}

a:hover {{
    background-color: {bg};
}}

code, tt, pre.literal-block, pre.doctest-block {{
    font-family: monospace;
    background-color: {bg};
}}
