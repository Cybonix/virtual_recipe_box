from fpdf import FPDF
import requests
import boto3
import uuid
import PyPDF2
import os

# AWS Clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# DynamoDB Table
table_name = 'Recipes'
table = dynamodb.Table(table_name)

# S3 Bucket
bucket_name = 'recipe-box-storage'

def main_menu():
    """Displays the main menu and routes user input to the correct functionality."""
    while True:
        print("\n--- Virtual Recipe Box ---")
        print("1. Add a Recipe Manually")
        print("2. Upload and Process a Recipe PDF")
        print("3. Search Recipes")
        print("4. Edit a Recipe")
        print("5. Delete a Recipe")
        print("6. Export Recipe to S3")
        print("7. Exit")
        
        choice = input("Select an option (1-7): ")
        
        if choice == '1':
            add_recipe_manual()
        elif choice == '2':
            upload_recipe_pdf()
        elif choice == '3':
            search_recipes()
        elif choice == '4':
            edit_recipe()
        elif choice == '5':
            delete_recipe()
        elif choice == '6':
            export_recipe_to_s3()
        elif choice == '7':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

def add_recipe_manual():
    """Allows the user to manually add a recipe and upload an associated image."""
    print("\n-- Add a New Recipe --")
    recipe_name = input("Enter recipe name: ")
    ingredients = input("Enter ingredients (comma-separated): ")

    # Provide clear guidance for entering instructions
    print("\nEnter cooking instructions, one step at a time.")
    print("Type each step and press Enter. When you're done, type 'done' and press Enter.")
    instructions = []
    while True:
        step = input(f"Step {len(instructions) + 1}: ")
        if step.lower() == 'done':
            break
        instructions.append(step)
    instructions_str = "\n".join(instructions)  # Combine steps into a single string

    tags = input("Enter tags (comma-separated): ")
    
    # Ask for an image file or URL
    image_input = input("Enter the full path of an image (JPG or PNG) or an image URL to associate with this recipe, or leave blank to skip: ").strip()
    image_s3_key = None

    if image_input:
        try:
            # Check if input is a URL
            if image_input.startswith('http://') or image_input.startswith('https://'):
                print("Downloading image from URL...")
                response = requests.get(image_input, stream=True)
                if response.status_code == 200:
                    # Save the image locally temporarily
                    image_local_path = f"/tmp/{recipe_name.replace(' ', '_')}.jpg"
                    with open(image_local_path, 'wb') as image_file:
                        for chunk in response.iter_content(1024):
                            image_file.write(chunk)
                    image_path = image_local_path
                else:
                    print("Failed to download image from URL. Skipping image upload.")
                    image_path = None
            else:
                # Use the provided local file path
                image_path = image_input

            # Upload image to S3
            if image_path and os.path.exists(image_path):
                image_s3_key = f"recipe_images/{recipe_name.replace(' ', '_')}_{str(uuid.uuid4())}.jpg"
                s3.upload_file(image_path, bucket_name, image_s3_key)
                print(f"Image uploaded to S3 with key: {image_s3_key}")
                # Clean up local downloaded image if applicable
                if image_path.startswith('/tmp/'):
                    os.remove(image_path)
            else:
                print("Error: Image file not found. Skipping image upload.")
        except Exception as e:
            print(f"Error uploading image to S3: {e}")
    
    # Generate a unique ID for the recipe
    recipe_id = str(uuid.uuid4())

    # Add recipe metadata to DynamoDB
    try:
        table.put_item(
            Item={
                'RecipeID': recipe_id,
                'RecipeName': recipe_name,
                'Ingredients': ingredients,
                'Instructions': instructions_str,
                'Tags': tags,
                'ImageS3Key': image_s3_key  # Save the S3 key for the image
            }
        )
        print(f"Recipe '{recipe_name}' added successfully!")
    except Exception as e:
        print(f"Error saving recipe to DynamoDB: {e}")

def upload_recipe_pdf():
    """Uploads a recipe PDF, processes its content, and stores metadata in DynamoDB."""
    print("\n-- Upload and Process a Recipe PDF --")
    file_path = input("Enter the full path of the PDF file: ")
    
    try:
        # Open the PDF file and extract text
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text()
        
        # Parse the text for recipe metadata
        print("\nExtracted Recipe Content:")
        print(extracted_text)
        
        recipe_name = input("\nEnter the recipe name (or leave blank to use extracted content): ")
        if not recipe_name:
            recipe_name = "Unnamed Recipe"
        ingredients = input("Enter ingredients (comma-separated, or leave blank if in PDF): ")
        instructions = input("Enter cooking instructions (or leave blank if in PDF): ")
        tags = input("Enter tags (comma-separated): ")
        
        recipe_id = str(uuid.uuid4())  # Unique ID for the recipe
        
        # Upload the PDF file to S3
        file_key = f"recipes/{recipe_id}.pdf"
        s3.upload_file(file_path, bucket_name, file_key)
        print(f"PDF uploaded to S3 with key: {file_key}")
        
        # Add recipe metadata to DynamoDB
        table.put_item(
            Item={
                'RecipeID': recipe_id,
                'RecipeName': recipe_name,
                'Ingredients': ingredients if ingredients else "See PDF",
                'Instructions': instructions if instructions else "See PDF",
                'Tags': tags,
                'PDFKey': file_key
            }
        )
        print("Recipe metadata saved to DynamoDB!")
    
    except FileNotFoundError:
        print("Error: File not found. Please check the path and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")

def search_recipes():
    """Searches recipes by name or tag."""
    print("\n-- Search Recipes --")
    search_term = input("Enter recipe name or tag to search: ")
    
    # Query DynamoDB for recipes
    response = table.scan()
    recipes = [item for item in response['Items'] if search_term.lower() in item.get('RecipeName', '').lower() or search_term.lower() in item.get('Tags', '').lower()]
    
    if recipes:
        print(f"\nFound {len(recipes)} recipe(s):")
        for recipe in recipes:
            print(f" - {recipe['RecipeName']} (ID: {recipe['RecipeID']})")
    else:
        print("No recipes found.")

def edit_recipe():
    """Edits an existing recipe's details."""
    print("\n-- Edit a Recipe --")
    recipe_id = input("Enter Recipe ID to edit: ")
    
    try:
        # Fetch the recipe from DynamoDB
        response = table.get_item(Key={'RecipeID': recipe_id})
        if 'Item' not in response:
            print(f"No recipe found with ID: {recipe_id}")
            return
        
        recipe = response['Item']
        print(f"Editing recipe: {recipe['RecipeName']}")

        # Display current details
        print("\nCurrent Details:")
        print(f"Name: {recipe['RecipeName']}")
        print(f"Ingredients: {recipe['Ingredients']}")
        print(f"Instructions: {recipe['Instructions']}")
        print(f"Tags: {recipe['Tags']}")
        if recipe.get('ImageS3Key'):
            print(f"Image S3 Key: {recipe['ImageS3Key']}")

        # Prompt for updates
        new_name = input(f"Enter new name (or press Enter to keep '{recipe['RecipeName']}'): ").strip()
        new_ingredients = input(f"Enter new ingredients (comma-separated, or press Enter to keep current): ").strip()

        # Handle instructions step-by-step
        print("\nEditing Instructions. Press Enter to keep a step as is. Type 'remove' to delete a step. Add new steps at the end.")
        current_instructions = recipe['Instructions'].split('\n')
        updated_instructions = []
        for idx, step in enumerate(current_instructions, 1):
            updated_step = input(f"Step {idx}: {step} (Edit or press Enter to keep): ").strip()
            if updated_step.lower() == 'remove':
                continue  # Skip this step (delete it)
            elif updated_step:
                updated_instructions.append(updated_step)
            else:
                updated_instructions.append(step)  # Keep the existing step

        # Add new steps
        print("Add new steps. Type 'done' when you're finished.")
        while True:
            new_step = input(f"Step {len(updated_instructions) + 1}: ").strip()
            if new_step.lower() == 'done':
                break
            updated_instructions.append(new_step)

        # Combine steps into a single string
        updated_instructions_str = "\n".join(updated_instructions)

        new_tags = input(f"Enter new tags (comma-separated, or press Enter to keep current): ").strip()
        new_image = input("Enter new image path (JPG or PNG) or URL, or press Enter to keep current: ").strip()

        # Prepare the updated fields
        updated_fields = {}
        if new_name:
            updated_fields['RecipeName'] = new_name
        if new_ingredients:
            updated_fields['Ingredients'] = new_ingredients
        if updated_instructions_str:
            updated_fields['Instructions'] = updated_instructions_str
        if new_tags:
            updated_fields['Tags'] = new_tags

        # Handle new image upload (same logic as before)
        if new_image:
            try:
                image_s3_key = f"recipe_images/{(new_name or recipe['RecipeName']).replace(' ', '_')}_{str(uuid.uuid4())}.jpg"
                if new_image.startswith('http://') or new_image.startswith('https://'):
                    print("Downloading new image from URL...")
                    response = requests.get(new_image, stream=True)
                    if response.status_code == 200:
                        image_local_path = f"/tmp/{os.path.basename(image_s3_key)}"
                        with open(image_local_path, 'wb') as image_file:
                            for chunk in response.iter_content(1024):
                                image_file.write(chunk)
                        s3.upload_file(image_local_path, bucket_name, image_s3_key)
                        os.remove(image_local_path)
                    else:
                        print("Failed to download new image from URL.")
                        image_s3_key = recipe.get('ImageS3Key')
                else:
                    if os.path.exists(new_image):
                        s3.upload_file(new_image, bucket_name, image_s3_key)
                    else:
                        print("New image file not found. Keeping current image.")
                        image_s3_key = recipe.get('ImageS3Key')
                updated_fields['ImageS3Key'] = image_s3_key
            except Exception as e:
                print(f"Error uploading new image: {e}")

        # Update the recipe in DynamoDB
        if updated_fields:
            update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in updated_fields.keys())
            expression_attribute_values = {f":{k}": v for k, v in updated_fields.items()}
            table.update_item(
                Key={'RecipeID': recipe_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            print(f"Recipe '{recipe_id}' updated successfully!")
        else:
            print("No updates made.")

    except Exception as e:
        print(f"An error occurred: {e}")

def delete_recipe():
    """Deletes a recipe and its associated files from DynamoDB and S3."""
    print("\n-- Delete a Recipe --")
    recipe_id = input("Enter Recipe ID to delete: ")
    
    try:
        # Fetch the recipe from DynamoDB
        response = table.get_item(Key={'RecipeID': recipe_id})
        if 'Item' not in response:
            print(f"No recipe found with ID: {recipe_id}")
            return
        
        recipe = response['Item']
        print(f"Recipe found: {recipe['RecipeName']}")
        print(f"Ingredients: {recipe['Ingredients']}")
        print(f"Instructions: {recipe['Instructions']}")
        print(f"Tags: {recipe['Tags']}")
        if recipe.get('ImageS3Key'):
            print(f"Image S3 Key: {recipe['ImageS3Key']}")
        if recipe.get('PDFKey'):
            print(f"Uploaded PDF S3 Key: {recipe['PDFKey']}")

        # Confirm deletion
        confirm = input("Are you sure you want to delete this recipe? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Deletion cancelled.")
            return

        # Delete the associated image from S3 (if exists)
        if recipe.get('ImageS3Key'):
            try:
                s3.delete_object(Bucket=bucket_name, Key=recipe['ImageS3Key'])
                print("Associated image deleted from S3.")
            except Exception as e:
                print(f"Error deleting image from S3: {e}")

        # Delete the associated PDF from S3 (if exists)
        if recipe.get('PDFKey'):
            try:
                s3.delete_object(Bucket=bucket_name, Key=recipe['PDFKey'])
                print("Associated PDF deleted from S3.")
            except Exception as e:
                print(f"Error deleting PDF from S3: {e}")

        # Delete the recipe from DynamoDB
        table.delete_item(Key={'RecipeID': recipe_id})
        print(f"Recipe '{recipe['RecipeName']}' deleted successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        

class PDF(FPDF):
    """Custom class for generating PDF files with enhanced styling."""
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Recipe Export', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
def export_recipe_to_s3():
    """Exports a recipe to a PDF file or re-exports an uploaded PDF."""
    print("\n-- Export Recipe to S3 --")
    recipe_id = input("Enter Recipe ID to export: ")
    
    try:
        # Fetch the recipe from DynamoDB
        response = table.get_item(Key={'RecipeID': recipe_id})
        if 'Item' not in response:
            print(f"No recipe found with ID: {recipe_id}")
            return
        
        recipe = response['Item']
        print(f"Found recipe: {recipe['RecipeName']}")

        # Check if the recipe was uploaded via PDF
        uploaded_pdf_key = recipe.get('PDFKey')  # Correctly handle the field for uploaded PDFs
        if uploaded_pdf_key:
            print("Recipe was uploaded as a PDF. Re-exporting the original PDF...")
            
            # Download the uploaded PDF from S3
            original_pdf_path = f"/tmp/{os.path.basename(uploaded_pdf_key)}"
            s3.download_file(bucket_name, uploaded_pdf_key, original_pdf_path)

            # Rename the PDF to use the recipe name
            recipe_pdf_name = f"{recipe['RecipeName'].replace(' ', '_')}.pdf"
            renamed_pdf_path = f"/tmp/{recipe_pdf_name}"
            os.rename(original_pdf_path, renamed_pdf_path)

            # Re-upload the renamed PDF to the exports folder
            export_pdf_key = f"exports/{recipe_pdf_name}"
            s3.upload_file(renamed_pdf_path, bucket_name, export_pdf_key)
            print(f"Original uploaded PDF re-exported to S3 as: {recipe_pdf_name}")
            os.remove(renamed_pdf_path)
            return

        # If no uploaded PDF exists, generate a new PDF
        print("Generating a new PDF for manually entered recipe...")
        file_name = f"{recipe['RecipeName'].replace(' ', '_')}.pdf"
        pdf = PDF()
        pdf.add_page()

        # Recipe Name (Centered, Bold, Blue)
        pdf.set_text_color(0, 0, 255)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, recipe['RecipeName'], ln=True, align='C')

        # Add Image (if provided)
        image_s3_key = recipe.get('ImageS3Key')
        if image_s3_key:
            image_path = f"/tmp/{os.path.basename(image_s3_key)}"
            s3.download_file(bucket_name, image_s3_key, image_path)
            pdf.ln(5)
            pdf.image(image_path, x=60, w=90)  # Centered, scaled to fit
            pdf.ln(10)
            os.remove(image_path)

        # Ingredients Section
        pdf.set_text_color(0, 0, 0)  # Reset color to black
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Ingredients:", ln=True)
        pdf.set_font('Arial', '', 12)
        ingredients = recipe['Ingredients'].split(',')
        for ingredient in ingredients:
            pdf.cell(10)  # Indent for bullet point
            pdf.multi_cell(0, 10, f"- {ingredient.strip()}")
        
        pdf.ln(5)  # Add spacing

        # Instructions Section
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Instructions:", ln=True)
        pdf.set_font('Arial', '', 12)
        instructions = recipe['Instructions'].split('\n')
        for idx, instruction in enumerate(instructions, 1):
            pdf.multi_cell(0, 10, f"{idx}. {instruction.strip()}")

        # Save and upload the new PDF
        pdf.output(file_name)
        export_pdf_key = f"exports/{file_name}"
        s3.upload_file(file_name, bucket_name, export_pdf_key)
        print(f"Generated PDF uploaded to S3 at key: {export_pdf_key}")
        os.remove(file_name)

    except Exception as e:
        print(f"An error occurred: {e}")

# Start the application
if __name__ == "__main__":
    main_menu()
