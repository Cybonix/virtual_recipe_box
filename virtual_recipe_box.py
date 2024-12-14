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
    # ... rest of the code ...

def add_recipe_manual():
    """Allows the user to manually add a recipe and upload an associated image."""
    # ... rest of the code ...

def upload_recipe_pdf():
    """Uploads a recipe PDF, processes its content, and stores metadata in SQLite."""
    # ... rest of the code ...

def search_recipes():
    """Searches recipes by name or tag."""
    # ... rest of the code ...

def edit_recipe():
    """Edits an existing recipe's details."""
    # ... rest of the code ...

def delete_recipe():
    """Deletes a recipe and its associated files from SQLite."""
    # ... rest of the code ...

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

# ... rest of the code ...

# Close the SQLite connection when the application exits
atexit.register(conn.close)

# Start the application
if __name__ == "__main__":
    main_menu()
