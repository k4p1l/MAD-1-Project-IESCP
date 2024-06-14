from website import create_app

app = create_app()

# if __name__ == '__main__' is a condition which checks if the current module is the main module or not. 
# It is used to check if the current module is the main module or not.
# Python assigns the special name __main__ to the script being executed when it is run as the main program.

if __name__ == '__main__':
    app.run(debug=True)
