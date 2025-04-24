# def output_to_file(text_to_output, filename="log.txt", output_dir='../web_crawling/output/', mode='w'):
def output_to_file(text_to_output, filename="log.txt", output_dir='../../debug/', mode='w'):
    """
    Outputs a given string to a file at the specified path.

    Args:
        text_to_output: The string that you want to write to the file.
        filepath: The full path to the file where the string will be written.
                Defaults to 'output.txt' in the current directory if not specified.
    """
    text_to_output = str(text_to_output)

    try:
        with open(output_dir + filename, mode, encoding='UTF-8') as file:
            file.write(text_to_output)
            print(f"Successfully wrote to: {filename}")
    except Exception as e:
        print(f"An error occurred while writing to {filename}: {e}")