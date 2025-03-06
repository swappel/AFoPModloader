import os
import struct

print("Welcome to the modloader prototype!\nThis prototype features a first version of the data encoding algorithm to transform mods into files.\n"
"Version: 1.0.0-alpha")

print("Please enter your commmand below(enter \"help\" to display the help page):")
userinput = ""

def format_strings(original: str) -> str:
    """
    Used for formatting strings so they can be used as the file paths.

    Parameters:
    original: This takes the file to be formatted

    Returns: 
    str: This returns the formatted string
    """

    return original.rstrip("/\\")

def display_help():
    """
    This function prints the help documentation.
    """

    print("Help:\n"
    "dec <mod directory> <destination directory> : Decompiles the mod and outputs it to the destination directory (USUALLY MULTIPLE FOLDERS)\n"
    "enc <mod directory(root folder)> <mod name> <output folder> : Outputs the compiled mod in the output directory.\n"
    "debug [mod directory] : Shows important information about a compiled mod\n"
    "help : Shows this page")

def encode(mod_directory: str, mod_name: str) -> None:
    """
    Encodes the mod root directory into a single file that can be read and/or decompiles by the modloader itself.
    
    Parameters:
    mod_directory: This parameter takes the root folder of the to be compiled mod
    output_directory: This parameter takes the output directory that the mod is supposed to be compiled into
    mod_name: This paraleter uses the mod name and uses it as the final file name
    """
    
    final_directory = mod_name

    with open(final_directory, "wb") as archive:
        for foldername, _, filenames in os.walk(mod_directory):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                relative_path = os.path.relpath(file_path, mod_directory).encode('utf-8')

                with open(file_path, 'rb') as f:
                    file_data = f.read()

                # Writing the files header in the following format:
                # relative_path_length, file_size, relative_path
                archive.write(struct.pack("I", len(relative_path))) # '-byte relative path
                archive.write(struct.pack("Q", len(file_data))) # 8-byte file size
                archive.write(relative_path) # Actual file path
                archive.write(file_data) # File content

    print(f"Files successfuly packed into: {final_directory}")

def decode(mod_directory: str, output_directory: str) -> None:
    """
    Decodes the mod files to their root directories. Defaults to real-name folders

    Parameters: 
    mod_directory: The mod file to be decoded into readable text
    output_directory: The directory the contained files will be sent to
    """
    
    with open(mod_directory, "rb") as archive:
        while True:
            # Red 4-byte relative path length
            path_len_data = archive.read(4)
            
            # True if no more data to read
            if not path_len_data:
                break

            path_len = struct.unpack("I", path_len_data)[0]

            #Read the 8-byte file size
            file_size = struct.unpack("Q", archive.read(8))[0]

            # Read the relative path
            relative_path = archive.read(path_len).decode('utf-8')
            output_path = os.path.join(output_directory, relative_path)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Read file content and write to output path
            with open(output_path, "wb") as f:
                f.write(archive.read(file_size))

    print(f"Deoded mod to {output_directory}")

while (True):
    print(">>>", end=" ")
    user_input = input()
    user_arguments = user_input.split(" ")

    if user_input.startswith("help"):
        display_help()
    elif user_input.startswith("enc") or user_input.startswith("encode"):
        print(len(user_arguments), user_arguments)
        if len(user_arguments) == 3:
            encode(user_arguments[1], user_arguments[2])
        else:
            print("Wrong format for this command. Please check help documentation for the correct format.")
            continue
    elif user_input.startswith("dec") or user_input.startswith("decode"):
        if len(user_arguments) == 3:
            decode(user_arguments[1], user_arguments[2])
        else:
            print("Incorrect format of the command. Please reffer to the documentation from the help command")
    else:
        print(f"Command \"{user_arguments[0]}\" not recognized. Please try again.")
