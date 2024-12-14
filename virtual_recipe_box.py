from fpdf import FPDF
import requests
import uuid
import PyPDF2
import os
import sqlite3
import atexit
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

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
    try:
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
    except Exception as e:
        logging.error(f"Error adding recipe manually: {e}")
        print("An error occurred while adding the recipe. Please try again.")

# ... rest of the code ...
