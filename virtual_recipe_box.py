from fpdf import FPDF
import requests
import uuid
import PyPDF2
import os
import sqlite3

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

    # Save the image locally
    if image_path and os.path.exists(image_path):
        image_local_path = f"images/{recipe_name.replace(' ', '_')}_{str(uuid.uuid4())}.jpg"
        os.makedirs(os.path.dirname(image_local_path), exist_ok=True)
        with open(image_local_path, 'wb') as image_file:
            image_file.write(requests.get(image_input).content)
        image_path = image_local_path

    # Add recipe metadata to SQLite
    try:
        cursor.execute('''
            INSERT INTO Recipes (RecipeID, RecipeName, Ingredients, Instructions, Tags, ImagePath)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (recipe_id, recipe_name, ingredients, instructions_str, tags, image_path))
        conn.commit()
        print(f"Recipe '{recipe_name}' added successfully!")
    except Exception as e:
        print(f"Error saving recipe to SQLite: {e}")

def upload_recipe_pdf():
    """Uploads a recipe PDF, processes its content, and stores metadata in SQLite."""
    # ... rest of the code ...

    # Save the PDF locally
    pdf_local_path = f"pdfs/{recipe_id}.pdf"
    os.makedirs(os.path.dirname(pdf_local_path), exist_ok=True)
    with open(pdf_local_path, 'wb') as pdf_file:
        pdf_file.write(open(file_path, 'rb').read())

    # Add recipe metadata to SQLite
    try:
        cursor.execute('''
            INSERT INTO Recipes (RecipeID, RecipeName, Ingredients, Instructions, Tags, PDFPath)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (recipe_id, recipe_name, ingredients, instructions, tags, pdf_local_path))
        conn.commit()
        print("Recipe metadata saved to SQLite!")
    except Exception as e:
        print(f"Error saving recipe to SQLite: {e}")

def search_recipes():
    """Searches recipes by name or tag."""
    # ... rest of the code ...

    # Query SQLite for recipes
    cursor.execute('''
        SELECT * FROM Recipes
        WHERE RecipeName LIKE ? OR Tags LIKE ?
    ''', (f"%{search_term}%", f"%{search_term}%"))
    recipes = cursor.fetchall()

    # ... rest of the code ...

def edit_recipe():
    """Edits an existing recipe's details."""
    # ... rest of the code ...

    # Update the recipe in SQLite
    if updated_fields:
        update_query = f"UPDATE Recipes SET {', '.join(f'{k} = ?' for k in updated_fields.keys())} WHERE RecipeID = ?"
        cursor.execute(update_query, (*updated_fields.values(), recipe_id))
        conn.commit()
        print(f"Recipe '{recipe_id}' updated successfully!")
    else:
        print("No updates made.")

def delete_recipe():
    """Deletes a recipe and its associated files from SQLite."""
    # ... rest of the code ...

    # Delete the associated image from the local file system (if exists)
    if recipe.get('ImagePath'):
        try:
            os.remove(recipe['ImagePath'])
            print("Associated image deleted from local file system.")
        except Exception as e:
            print(f"Error deleting image from local file system: {e}")

    # Delete the associated PDF from the local file system (if exists)
    if recipe.get('PDFPath'):
        try:
            os.remove(recipe['PDFPath'])
            print("Associated PDF deleted from local file system.")
        except Exception as e:
            print(f"Error deleting PDF from local file system: {e}")

    # Delete the recipe from SQLite
    cursor.execute('DELETE FROM Recipes WHERE RecipeID = ?', (recipe_id,))
    conn.commit()
    print(f"Recipe '{recipe['RecipeName']}' deleted successfully!")

# ... rest of the code ...

# Close the SQLite connection when the application exits
atexit.register(conn.close)

# Start the application
if __name__ == "__main__":
    main_menu()
