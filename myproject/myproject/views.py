#from django.http import HttpResponse
from django.shortcuts import render
import subprocess

def homepage(request):
    #return HttpResponse("Hello World!")
    return render(request, 'home.html')

def about(request):
    #return HttpResponse("My About Page.")
    return render(request, 'about.html')

def lexical_analyzer(request):
    result = None
    user_input = ''
    if request.method == 'POST':
        # Retrieve the content from the textarea field
        user_input = request.POST.get('user_input', '').strip() # 'user_input' matches the name attribute of the textarea
        if user_input:
            try:
                # Run the Python script with the input as an argument
                script_path = 'C:\\Users\\Abram\Documents\\1st Sem (3rd Year College)\\Principles of Programming Languages\\JARGEN\\JARGEN\\syntax.analyzer\\main.py'  # Replace with the actual path
                process = subprocess.run(
                    ['python', script_path, user_input],
                    capture_output=True,
                    text=True
                )
                # Capture the script's output
                result = process.stdout.strip() if process.returncode == 0 else process.stderr.strip()
            except Exception as e:
                result = f"An error occurred: {e}"
    
    return render(request, 'syntax-analyzer.html', {'user_input': user_input, 'result': result})
