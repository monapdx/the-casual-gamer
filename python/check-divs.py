def check_div_balance(html_file):
    with open(html_file, 'r') as file:
        html_content = file.read()

    # Initialize a stack to keep track of <div> tags
    stack = []
    # Counter for line numbers
    line_number = 1
    unbalanced = False

    # Split content by lines for better debugging
    for line in html_content.splitlines():
        # Check for opening and closing <div> tags
        open_divs = line.count('<div')
        close_divs = line.count('</div>')

        # Push each opening <div> onto the stack
        stack.extend([line_number] * open_divs)

        # Pop the stack for each closing </div>
        for _ in range(close_divs):
            if stack:
                stack.pop()
            else:
                print(f"Unmatched closing </div> at line {line_number}")
                unbalanced = True

        line_number += 1

    # After reading through the file, check if the stack is empty
    if stack:
        print("Unmatched opening <div> at lines:", ', '.join(map(str, stack)))
        unbalanced = True

    if not unbalanced:
        print("All <div> tags are balanced.")
    else:
        print("There are unbalanced <div> tags in the file.")

# Usage example
check_div_balance("C:\\Users\\Ash\\Downloads\\Code\\ebook.html")
