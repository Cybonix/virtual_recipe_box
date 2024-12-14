from fpdf import FPDF
import requests
import uuid
import PyPDF2
import os
import sqlite3
import atexit

# SQLite Database Connection
conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()

# Create the Recipes table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Recipes (
        RecipeID TEXT PRIMARY KEY,
        RecipeName TEXT,
        Ingredients TEXT,
        Instructions TEXT,
        Tags TEXT,
        ImagePath TEXT,
        PDFPath TEXT
    )
''')
conn.commit()

def main_menu():
    """Displays the main menu and routes user input to the correct functionality."""
    while True:
        print("\nVirtual Recipe Box")
        print("1. Add Recipe Manually")
        print("2. Upload Recipe PDF")
        print("3. Search Recipes")
        print("4. Edit Recipe")
        print("5. Delete Recipe")
        print("6. Export Recipe to PDF")
        print("7. Quit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_recipe_manual()
        elif choice == "2":
            upload_recipe_pdf()
        elif choice == "3":
            search_recipes()
        elif choice == "4":
            edit_recipe()
        elif choice == "5":
            delete_recipe()
        elif choice == "6":
            recipe_id = input("Enter the Recipe ID: ")
            export_recipe_to_pdf(recipe_id)
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please try again.")

def add_recipe_manual():
    """Allows the user to manually add a recipe and upload an associated image."""
    recipe_id = str(uuid.uuid4())
    recipe_name = input("Enter the recipe name: ")
    ingredients = input("Enter the ingredients: ")
    instructions = input("Enter the instructions: ")
    tags = input("Enter the tags (comma-separated): ")
    image_path = input("Enter the path to the image file: ")

    cursor.execute('''
        INSERT INTO Recipes (RecipeID, RecipeName, Ingredients, Instructions, Tags, ImagePath)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (recipe_id, recipe_name, ingredients, instructions, tags, image_path))
    conn.commit()

    print(f"Recipe '{recipe_name}' added successfully with ID: {recipe_id}")

def upload_recipe_pdf():
    """Uploads a recipe PDF, processes its content, and stores metadata in SQLite."""
    pdf_path = input("Enter the path to the recipe PDF file: ")

    # Extract text from the PDF
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page_num).extractText()

    # Process the extracted text to extract recipe details
    # This part is application-specific and may require custom parsing logic
    # For simplicity, let's assume the text contains the recipe name, ingredients, instructions, and tags
    recipe_name = input("Enter the recipe name: ")
    ingredients = input("Enter the ingredients: ")
    instructions = input("Enter the instructions: ")
    tags = input("Enter the tags (comma-separated): ")

    recipe_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO Recipes (RecipeID, RecipeName, Ingredients, Instructions, Tags, PDFPath)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (recipe_id, recipe_name, ingredients, instructions, tags, pdf_path))
    conn.commit()

    print(f"Recipe '{recipe_name}' added successfully with ID: {recipe_id}")

def search_recipes():
    """Searches recipes by name or tag."""
    search_term = input("Enter the recipe name or tag to search for: ")

    cursor.execute('''
        SELECT * FROM Recipes
        WHERE RecipeName LIKE ? OR Tags LIKE ?
    ''', (f"%{search_term}%", f"%{search_term}%"))
    recipes = cursor.fetchall()

    if not recipes:
        print("No recipes found.")
    else:
        print("Found recipes:")
        for recipe in recipes:
            print(f"ID: {recipe[0]}, Name: {recipe[1]}")

def edit_recipe():
    """Edits an existing recipe's details."""
    recipe_id = input("Enter the Recipe ID: ")

    cursor.execute('SELECT * FROM Recipes WHERE RecipeID = ?', (recipe_id,))
    recipe = cursor.fetchone()

    if recipe is None:
        print(f"Recipe with ID '{recipe_id}' not found.")
        return

    print(f"Editing recipe: {recipe[1]}")
    recipe_name = input("Enter the new recipe name (leave blank to keep current): ")
    ingredients = input("Enter the new ingredients (leave blank to keep current): ")
    instructions = input("Enter the new instructions (leave blank to keep current): ")
    tags = input("Enter the new tags (comma-separated, leave blank to keep current): ")
    image_path = input("Enter the new path to the image file (leave blank to keep current): ")

    if not recipe_name:
        recipe_name = recipe[1]
    if not ingredients:
        ingredients = recipe[2]
    if not instructions:
        instructions = recipe[3]
    if not tags:
        tags = recipe[4]
    if not image_path:
        image_path = recipe[5]

    cursor.execute('''
        UPDATE Recipes
        SET RecipeName = ?, Ingredients = ?, Instructions = ?, Tags = ?, ImagePath = ?
        WHERE RecipeID = ?
    ''', (recipe_name, ingredients, instructions, tags, image_path, recipe_id))
    conn.commit()

    print(f"Recipe '{recipe_name}' updated successfully.")

def delete_recipe():
    """Deletes a recipe and its associated files from SQLite."""
    recipe_id = input("Enter the Recipe ID: ")

    cursor.execute('SELECT * FROM Recipes WHERE RecipeID = ?', (recipe_id,))
    recipe = cursor.fetchone()

    if recipe is None:
        print(f"Recipe with ID '{recipe_id}' not found.")
        return

    cursor.execute('DELETE FROM Recipes WHERE RecipeID = ?', (recipe_id,))
    conn.commit()

    print(f"Recipe '{recipe[1]}' deleted successfully.")

def export_recipe_to_pdf(recipe_id):
    """Exports a recipe to a nicely formatted PDF file."""
    # Query SQLite for the recipe
    cursor.execute('SELECT * FROM Recipes WHERE RecipeID = ?', (recipe_id,))
    recipe = cursor.fetchone()

    if recipe is None:
        print(f"Recipe with ID '{recipe_id}' not found.")
        return

    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()

    # Set font and add recipe details to the PDF
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=recipe[1], ln=1, align='C')  # Recipe Name
    pdf.image(recipe[5], x=10, y=30, w=190)  # Image
    pdf.multi_cell(0, 10, txt=f"Ingredients:\n{recipe[2]}")  # Ingredients
    pdf.multi_cell(0, 10, txt=f"Instructions:\n{recipe[3]}")  # Instructions
    pdf.multi_cell(0, 10, txt=f"Tags:\n{recipe[4]}")  # Tags

    # Save the PDF to the local file system
    pdf_local_path = f"exports/{recipe[1].replace(' ', '_')}_{recipe_id}.pdf"
    os.makedirs(os.path.dirname(pdf_local_path), exist_ok=True)
    pdf.output(pdf_local_path)

    print(f"Recipe '{recipe[1]}' exported to PDF: {pdf_local_path}")

# Close the SQLite connection when the application exits
atexit.register(conn.close)

# Start the application
if __name__ == "__main__":
    main_menu()
